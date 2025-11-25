"""
Utility helpers around encrypting/decrypting todo data with 'per task' keys.

The module currently uses Fernet (AES128-CBC + HMAC) from the cryptography
package. This was chosen as it provides authenticated encryption with minimal boilerplate.
"""

from __future__ import annotations

from typing import Optional

from cryptography.fernet import Fernet, InvalidToken


def generate_data_key() -> bytes:
    """Return a fresh symmetric key (base64 url-safe bytes) for a todo item."""
    return Fernet.generate_key()


def encrypt_message(plaintext: Optional[str], data_key: bytes) -> str:
    """
    Encrypt a plaintext message with the provided data key.
    Returns a UTF-8 string ready to be stored in the database.
    """
    if plaintext is None:
        plaintext = ""
    
    if not isinstance(plaintext, str):
        raise TypeError("Plaintext must be a string or None")
    
    if not data_key:
        raise ValueError("A data key is required to encrypt messages")
    
    fernet = Fernet(data_key)
    ciphertext = fernet.encrypt(plaintext.encode("utf-8"))
    return ciphertext.decode("utf-8")


def decrypt_message(ciphertext: str, data_key: bytes) -> str:
    """Reverse of encrypt_message, returning the original plaintext string."""
    if not ciphertext:
        return ""
    
    if not data_key:
        raise ValueError("A data key is required to decrypt messages")
    
    fernet = Fernet(data_key)
    try:
        plaintext = fernet.decrypt(ciphertext.encode("utf-8"))
    except InvalidToken as exc:
        raise ValueError("Ciphertext cannot be decrypted with the supplied key") from exc
    
    return plaintext.decode("utf-8")
