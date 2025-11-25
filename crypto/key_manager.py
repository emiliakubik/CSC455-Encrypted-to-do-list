"""
Key derivation utilities to make it easy to encrypt todo data for multiple users.

Each todo has its own random data key, in order
to give multiple users access, we need to store that data key encrypted for every
collaborator. Rather than asking users to manage their own keys, we derive a
stable per-user key from a master secret using HMAC-SHA256.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from pathlib import Path
from typing import Optional

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

MASTER_KEY_ENV_VAR = "TODO_MASTER_KEY_PATH"
DEFAULT_MASTER_KEY_PATH = Path("crypto/master.key")

NONCE_BYTES = 12
TAG_BYTES = 16

_master_key_cache: Optional[bytes] = None


def _get_master_key_path() -> Path:
    override = os.getenv(MASTER_KEY_ENV_VAR)
    if override:
        return Path(override)
    return DEFAULT_MASTER_KEY_PATH


def reset_master_key_cache() -> None:
    """Test helper to drop the cached master key so a new one can be loaded."""
    global _master_key_cache
    _master_key_cache = None


def _load_or_create_master_key() -> bytes:
    """
    Load the master key from disk, creating it if the file does not exist yet.
    The master key is stored in url-safe base64 so the file is text friendly.
    """
    global _master_key_cache
    if _master_key_cache is not None:
        return _master_key_cache
    
    path = _get_master_key_path()
    if path.exists():
        raw = path.read_bytes()
        try:
            _master_key_cache = base64.urlsafe_b64decode(raw)
            return _master_key_cache
        except Exception as exc:  
            raise ValueError(f"Failed to load master key from {path}") from exc
    
    path.parent.mkdir(parents=True, exist_ok=True)
    master_key = os.urandom(32)
    encoded = base64.urlsafe_b64encode(master_key)
    path.write_bytes(encoded)
    try:
        os.chmod(path, 0o600)
    except OSError:
        #on some OS (e.g. Windows) chmod may fail; not critical for functionality.
        pass
    
    _master_key_cache = master_key
    return master_key


def derive_user_key(user_id: int) -> bytes:
    """
    Derive a stable user specific key
    """
    if user_id is None:
        raise ValueError("user_id is required to derive a user key")
    
    master_key = _load_or_create_master_key()
    message = str(int(user_id)).encode("utf-8")
    digest = hmac.new(master_key, message, hashlib.sha256).digest()
    return digest


def encrypt_data_key_for_user(user_id: int, data_key: bytes) -> str:
    """
    Encrypt the todo data key for a specific user so it can be stored safely.
    Returns the ciphertext as a UTF-8 string for database storage.
    """
    if isinstance(data_key, str):
        payload = data_key.encode("utf-8")
    else:
        payload = data_key
    
    user_key = derive_user_key(user_id)
    nonce = get_random_bytes(NONCE_BYTES)
    cipher = AES.new(user_key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(payload)
    token = base64.urlsafe_b64encode(nonce + tag + ciphertext)
    return token.decode("utf-8")


def decrypt_data_key_for_user(user_id: int, encrypted_key: str) -> bytes:
    """Decrypt the todo data key for a user, returning the raw key bytes."""
    user_key = derive_user_key(user_id)
    try:
        raw = base64.urlsafe_b64decode(encrypted_key.encode("utf-8"))
    except Exception as exc:
        raise ValueError("Encrypted key is not valid base64") from exc
    
    if len(raw) < NONCE_BYTES + TAG_BYTES:
        raise ValueError("Encrypted key payload is too short")
    
    nonce = raw[:NONCE_BYTES]
    tag = raw[NONCE_BYTES:NONCE_BYTES + TAG_BYTES]
    ciphertext = raw[NONCE_BYTES + TAG_BYTES :]
    
    cipher = AES.new(user_key, AES.MODE_GCM, nonce=nonce)
    try:
        return cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError as exc:
        raise ValueError("Encrypted key cannot be decrypted for this user") from exc
