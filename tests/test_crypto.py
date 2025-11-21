import base64

import pytest

from crypto import encryption, key_manager


@pytest.fixture(autouse=True)
def temp_master_key(tmp_path, monkeypatch):
    """Force key material into the tmp path so tests do not touch the real key."""
    key_path = tmp_path / "test_master.key"
    monkeypatch.setenv(key_manager.MASTER_KEY_ENV_VAR, str(key_path))
    key_manager.reset_master_key_cache()
    yield


def test_encrypt_decrypt_round_trip():
    data_key = encryption.generate_data_key()
    plaintext = "Top secret todo"
    ciphertext = encryption.encrypt_message(plaintext, data_key)
    
    assert ciphertext != plaintext
    decrypted = encryption.decrypt_message(ciphertext, data_key)
    assert decrypted == plaintext


def test_each_user_gets_unique_key_material():
    key_manager.reset_master_key_cache()
    user_key_1 = key_manager.derive_user_key(1)
    user_key_2 = key_manager.derive_user_key(2)
    
    assert user_key_1 != user_key_2
    # Fernet keys are base64 encoded 32-byte values.
    assert len(base64.urlsafe_b64decode(user_key_1)) == 32


def test_encrypted_data_key_round_trip():
    data_key = encryption.generate_data_key()
    encrypted_key = key_manager.encrypt_data_key_for_user(5, data_key)
    recovered = key_manager.decrypt_data_key_for_user(5, encrypted_key)
    assert recovered == data_key
    
    with pytest.raises(ValueError):
        key_manager.decrypt_data_key_for_user(6, encrypted_key)
