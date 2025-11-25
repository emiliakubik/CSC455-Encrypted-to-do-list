import hashlib
import hmac
import secrets
from typing import Optional, Tuple

from database.models import User

PBKDF2_ALGORITHM = "sha256"
PBKDF2_ITERATIONS = 200_000
PBKDF2_SALT_BYTES = 16
HASH_PREFIX = "pbkdf2_sha256"


def hash_password(password: str) -> str:
    """
    Hash a password using with random salt,
    returns a self contained string that stores the parameters needed for verification.
    """
    if not isinstance(password, str):
        raise TypeError("Password must be a string")
    
    if password == "":
        raise ValueError("Password cannot be empty")
    
    salt = secrets.token_bytes(PBKDF2_SALT_BYTES)
    derived_key = hashlib.pbkdf2_hmac(
        PBKDF2_ALGORITHM,
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    
    return f"{HASH_PREFIX}${PBKDF2_ITERATIONS}${salt.hex()}${derived_key.hex()}"


def verify_password(password: str, stored_value: str) -> Tuple[bool, Optional[str]]:
    """
    Verify password against the stored hash.
    
    """
    if not isinstance(password, str):
        return False, None
    
    if not stored_value:
        return False, None
    
    if stored_value.startswith(f"{HASH_PREFIX}$"):
        try:
            _, iteration_str, salt_hex, hash_hex = stored_value.split("$", 3)
            iterations = int(iteration_str)
            salt = bytes.fromhex(salt_hex)
            stored_hash = bytes.fromhex(hash_hex)
        except (ValueError, TypeError):
            return False, None
        
        candidate_hash = hashlib.pbkdf2_hmac(
            PBKDF2_ALGORITHM,
            password.encode("utf-8"),
            salt,
            iterations,
        )
        return hmac.compare_digest(candidate_hash, stored_hash), None
    
    # Legacy plaintext storage fallback
    if stored_value == password:
        upgraded_hash = hash_password(password)
        return True, upgraded_hash
    
    return False, None


def register_user(username, password):
    """
    Register a new user. 
    Returns (success, message, user_id).
    """
    # Basic input validation
    if not username or username.strip() == "":
        return False, "Username cannot be empty", None
    
    if len(username.strip()) < 3:
        return False, "Username must be at least 3 characters", None
    
    if len(username.strip()) > 50:
        return False, "Username too long (max 50 characters)", None
    
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters", None
    
    username = username.strip().lower()  # Normalize username
    password_hash = hash_password(password)
    
    # Attempt to create user
    user_id = User.create(username, password_hash)
    
    if user_id:
        return True, "User registered successfully", user_id
    else:
        return False, "Username already exists", None


def login_user(username, password):
    """
    Authenticate user login.
    Returns (success, message, user_data).
    """
    if not username or not password:
        return False, "Username and password required", None
    
    # Normalize username for lookup
    username = username.strip().lower()
    
    # Get user from database
    user_data = User.get_by_username(username)
    
    if not user_data:
        return False, "Invalid username", None
    
    # Validate hashed password (with legacy plaintext fallback)
    password_valid, upgraded_hash = verify_password(password, user_data['password_hash'])
    if password_valid:
        if upgraded_hash:
            User.update(user_data['user_id'], password_hash=upgraded_hash)
        
        # Remove password from returned data for security
        safe_user_data = {
            'user_id': user_data['user_id'],
            'username': user_data['username']
        }
        return True, "Login successful", safe_user_data
    
    return False, "Invalid password", None


def logout_user():
    """
    Handle user logout.
    Returns success message.
    Note: Session management will be enhanced later.
    """
    # For now, just return success message
    # Future: Clear session data, tokens, etc.
    return True, "Logout successful"


def validate_username(username):
    """
    Validate username format.
    Returns (is_valid, message).
    """
    if not username or username.strip() == "":
        return False, "Username cannot be empty"
    
    username = username.strip()
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username too long (max 50 characters)"
    
    # Check for valid characters (letters, numbers, underscore)
    import re
    if not re.match("^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, "Valid username"


def check_user_exists(username):
    """
    Check if username already exists.
    Returns True if exists, False otherwise.
    """
    if not username:
        return False
    
    username = username.strip().lower()
    user_data = User.get_by_username(username)
    return user_data is not None
