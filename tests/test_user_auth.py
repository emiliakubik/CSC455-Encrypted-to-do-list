import pytest

from core import user_auth
from core.user_auth import hash_password, login_user, register_user, verify_password
from database import db_setup
from database.models import User


@pytest.fixture(autouse=True)
def temp_database(tmp_path, monkeypatch):
    """
    Each test gets its own isolated SQLite DB file so that user registration/login
    can run without mutating the developer's local database.
    """
    test_db_path = tmp_path / "test_todo.db"
    monkeypatch.setattr(db_setup, "DATABASE_NAME", str(test_db_path))
    db_setup.initialize_database()
    yield


def test_hash_password_round_trip():
    password = "ComplexPass!23"
    stored = hash_password(password)
    
    assert stored.startswith(user_auth.HASH_PREFIX)
    assert verify_password(password, stored) == (True, None)
    assert verify_password("wrong-pass", stored) == (False, None)


def test_register_user_persists_hashed_password():
    success, _, user_id = register_user("SecureUser", "StrongPass!")
    
    assert success is True
    assert user_id is not None
    
    stored_user = User.get_by_username("secureuser")
    assert stored_user is not None
    assert stored_user["password_hash"].startswith(user_auth.HASH_PREFIX)
    assert verify_password("StrongPass!", stored_user["password_hash"]) == (True, None)


def test_login_user_upgrades_plaintext_password():
    # Manually insert a legacy plaintext password
    conn = db_setup.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        ("legacyuser", "letmein123"),
    )
    conn.commit()
    conn.close()
    
    success, _, user_data = login_user("legacyuser", "letmein123")
    assert success is True
    assert user_data["username"] == "legacyuser"
    
    # After login the password should have been upgraded to the hashed format.
    upgraded_user = User.get_by_username("legacyuser")
    assert upgraded_user["password_hash"].startswith(user_auth.HASH_PREFIX)
    assert verify_password("letmein123", upgraded_user["password_hash"]) == (True, None)
