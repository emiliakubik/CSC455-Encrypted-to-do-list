"""
Key derivation utilities to make it easy to encrypt todo data for multiple users.

Each todo has its own random data key (handled in crypto/encryption.py). In order
to give multiple users access we need to store that data key encrypted for every
collaborator. Rather than asking users to manage their own secrets, we derive a
stable per-user key from a master secret using HMAC-SHA256. The master secret is
stored on disk (crypto/master.key by default) and can be overridden through the
TODO_MASTER_KEY_PATH environment variable for tests/other environments.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

MASTER_KEY_ENV_VAR = "TODO_MASTER_KEY_PATH"
DEFAULT_MASTER_KEY_PATH = Path("crypto/master.key")

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
        except Exception as exc:  # pragma: no cover - defensive branch
            raise ValueError(f"Failed to load master key from {path}") from exc
    
    path.parent.mkdir(parents=True, exist_ok=True)
    master_key = os.urandom(32)
    encoded = base64.urlsafe_b64encode(master_key)
    path.write_bytes(encoded)
    try:
        os.chmod(path, 0o600)
    except OSError:
        # On some OS (e.g. Windows) chmod may fail; not critical for functionality.
        pass
    
    _master_key_cache = master_key
    return master_key


def derive_user_key(user_id: int) -> bytes:
    """
    Derive a stable user-specific key using HMAC(master_key, user_id).
    The output is encoded so it can be fed directly into Fernet.
    """
    if user_id is None:
        raise ValueError("user_id is required to derive a user key")
    
    master_key = _load_or_create_master_key()
    message = str(int(user_id)).encode("utf-8")
    digest = hmac.new(master_key, message, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest)


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
    encrypted = Fernet(user_key).encrypt(payload)
    return encrypted.decode("utf-8")


def decrypt_data_key_for_user(user_id: int, encrypted_key: str) -> bytes:
    """Decrypt the todo data key for a user, returning the raw key bytes."""
    user_key = derive_user_key(user_id)
    try:
        return Fernet(user_key).decrypt(encrypted_key.encode("utf-8"))
    except InvalidToken as exc:
        raise ValueError("Encrypted key cannot be decrypted for this user") from exc
