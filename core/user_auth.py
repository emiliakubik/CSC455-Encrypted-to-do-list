from database.models import User

def register_user(username, password):
    """
    Register a new user. 
    Returns (success, message, user_id).
    Note: Password hashing will be handled by another team member.
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
    
    # For now, store password as plain text (hashing will be added by crypto team)
    username = username.strip().lower()  # Normalize username
    
    # Attempt to create user
    user_id = User.create(username, password)
    
    if user_id:
        return True, "User registered successfully", user_id
    else:
        return False, "Username already exists", None


def login_user(username, password):
    """
    Authenticate user login.
    Returns (success, message, user_data).
    Note: Password verification will be enhanced by crypto team.
    """
    if not username or not password:
        return False, "Username and password required", None
    
    # Normalize username for lookup
    username = username.strip().lower()
    
    # Get user from database
    user_data = User.get_by_username(username)
    
    if not user_data:
        return False, "Invalid username", None
    
    # For now, simple password comparison (will be replaced with hash verification)
    if user_data['password_hash'] == password:
        # Remove password from returned data for security
        safe_user_data = {
            'user_id': user_data['user_id'],
            'username': user_data['username']
        }
        return True, "Login successful", safe_user_data
    else:
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