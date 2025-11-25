"""
Utility helpers around encrypting/decrypting todo data with per-task keys using
PyCryptodome's AES-GCM implementation for authenticated encryption.
"""

from __future__ import annotations

import base64
from typing import Optional

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

DATA_KEY_BYTES = 32  # AES-256
NONCE_BYTES = 12
TAG_BYTES = 16


def generate_data_key() -> bytes:
    """Return a fresh symmetric key for a todo item."""
    return get_random_bytes(DATA_KEY_BYTES)


def _normalize_data_key(data_key: bytes) -> bytes:
    if not isinstance(data_key, (bytes, bytearray)):
        raise TypeError("Data key must be raw bytes")
    length = len(data_key)
    if length not in (16, 24, 32):
        raise ValueError("Data key must be 16, 24, or 32 bytes for AES")
    return bytes(data_key)


def encrypt_message(plaintext: Optional[str], data_key: bytes) -> str:
    """
    Encrypt a plaintext message with the provided data key.
    Returns a UTF-8 string ready to be stored in the database.
    """
    if plaintext is None:
        plaintext = ""
    
    if not isinstance(plaintext, str):
        raise TypeError("Plaintext must be a string or None")
    
    key = _normalize_data_key(data_key)
    nonce = get_random_bytes(NONCE_BYTES)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode("utf-8"))
    payload = nonce + tag + ciphertext
    return base64.urlsafe_b64encode(payload).decode("utf-8")


def decrypt_message(ciphertext: str, data_key: bytes) -> str:
    """Reverse of encrypt_message, returning the original plaintext string."""
    if not ciphertext:
        return ""
    
    key = _normalize_data_key(data_key)
    try:
        raw = base64.urlsafe_b64decode(ciphertext.encode("utf-8"))
    except Exception as exc:
        raise ValueError("Ciphertext is not valid base64") from exc
    
    if len(raw) < NONCE_BYTES + TAG_BYTES:
        raise ValueError("Ciphertext payload is too short")
    
    nonce = raw[:NONCE_BYTES]
    tag = raw[NONCE_BYTES:NONCE_BYTES + TAG_BYTES]
    encrypted = raw[NONCE_BYTES + TAG_BYTES :]
    
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    try:
        plaintext = cipher.decrypt_and_verify(encrypted, tag)
    except ValueError as exc:
        raise ValueError("Ciphertext cannot be decrypted with the supplied key") from exc
    
    return plaintext.decode("utf-8")
