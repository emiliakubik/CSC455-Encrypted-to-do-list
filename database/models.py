# Data validation function
def validate_todo_data(title, details=None):
    """Validate todo input data. Returns (is_valid, message)"""
    if not title or title.strip() == "":
        return False, "Title cannot be empty"
    
    if len(title.strip()) > 200:
        return False, "Title too long (max 200 characters)"
    
    if details and len(details) > 1000:
        return False, "Details too long (max 1000 characters)"
    
    return True, "Valid"


class User:
    @staticmethod
    def create(username, password_hash):
        """Create a new user. Returns user_id if successful, None if username exists."""
        import sqlite3
        from database.db_setup import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                          (username, password_hash))
            conn.commit()
            user_id = cursor.lastrowid
            return user_id
        except sqlite3.IntegrityError:
            # Handles duplicate usernames (UNIQUE constraint violation)
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_username(username):
        """Get user data by username. Returns user dict or None if not found."""
        from database.db_setup import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id, username, password_hash FROM users WHERE username = ?', 
                      (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'user_id': row[0],
                'username': row[1],
                'password_hash': row[2]
            }
        return None

    @staticmethod
    def get_by_id(user_id):
        """Get user data by id. Returns user dict or None if not found."""
        from database.db_setup import get_connection

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT user_id, username, password_hash FROM users WHERE user_id = ?',
                      (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'user_id': row[0],
                'username': row[1],
                'password_hash': row[2]
            }
        return None
    
    @staticmethod
    def update(user_id, username=None, password_hash=None):
        """Update user info. Returns True if successful, False otherwise."""
        import sqlite3
        from database.db_setup import get_connection
        
        if not username and not password_hash:
            return False
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            if username and password_hash:
                cursor.execute('UPDATE users SET username = ?, password_hash = ? WHERE user_id = ?',
                              (username, password_hash, user_id))
            elif username:
                cursor.execute('UPDATE users SET username = ? WHERE user_id = ?',
                              (username, user_id))
            elif password_hash:
                cursor.execute('UPDATE users SET password_hash = ? WHERE user_id = ?',
                              (password_hash, user_id))
            
            conn.commit()
            return cursor.rowcount > 0  # True if row was updated
        except sqlite3.IntegrityError:
            # Handles duplicate usernames
            return False
        finally:
            conn.close()
    
    @staticmethod
    def delete(user_id):
        """Delete user. Returns True if successful, False otherwise."""
        from database.db_setup import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        conn.commit()
        success = cursor.rowcount > 0  # True if row was deleted
        conn.close()
        
        return success


class Todo:
    @staticmethod
    def create(title, details, created_by):
        """Create a new todo. Returns task_id if successful, None if validation fails."""
        # Validate data first
        is_valid, message = validate_todo_data(title, details)
        if not is_valid:
            return None
        
        from database.db_setup import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''INSERT INTO todos (title, details, created_by, updated_by) 
                         VALUES (?, ?, ?, ?)''', 
                      (title.strip(), details, created_by, created_by))
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()
        
        return task_id
    
    @staticmethod
    def get_by_id(task_id):
        """Get todo data by task_id. Returns todo dict or None if not found."""
        from database.db_setup import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''SELECT task_id, title, details, created_by, updated_by, 
                                created_at, updated_at, is_complete 
                         FROM todos WHERE task_id = ?''', (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'task_id': row[0],
                'title': row[1],
                'details': row[2],
                'created_by': row[3],
                'updated_by': row[4],
                'created_at': row[5],
                'updated_at': row[6],
                'is_complete': row[7]
            }
        return None
    
    @staticmethod
    def get_by_user(user_id):
        """Get all todos created by a user. Returns list of todo dicts."""
        from database.db_setup import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''SELECT task_id, title, details, created_by, updated_by, 
                                created_at, updated_at, is_complete 
                         FROM todos WHERE created_by = ?''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        todos = []
        for row in rows:
            todos.append({
                'task_id': row[0],
                'title': row[1],
                'details': row[2],
                'created_by': row[3],
                'updated_by': row[4],
                'created_at': row[5],
                'updated_at': row[6],
                'is_complete': row[7]
            })
        return todos
    
    @staticmethod
    def update(task_id, title=None, details=None, updated_by=None):
        """Update todo info. Returns True if successful, False otherwise."""
        from database.db_setup import get_connection
        
        if not title and not details:
            return False
        
        conn = get_connection()
        cursor = conn.cursor()
        
        if title and details:
            cursor.execute('''UPDATE todos SET title = ?, details = ?, updated_by = ?, 
                             updated_at = CURRENT_TIMESTAMP WHERE task_id = ?''',
                          (title, details, updated_by, task_id))
        elif title:
            cursor.execute('''UPDATE todos SET title = ?, updated_by = ?, 
                             updated_at = CURRENT_TIMESTAMP WHERE task_id = ?''',
                          (title, updated_by, task_id))
        elif details:
            cursor.execute('''UPDATE todos SET details = ?, updated_by = ?, 
                             updated_at = CURRENT_TIMESTAMP WHERE task_id = ?''',
                          (details, updated_by, task_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    @staticmethod
    def delete(task_id):
        """Delete todo. Returns True if successful, False otherwise."""
        from database.db_setup import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM todos WHERE task_id = ?', (task_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    @staticmethod
    def mark_complete(task_id, updated_by=None):
        """Mark todo as complete. Returns True if successful, False otherwise."""
        from database.db_setup import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''UPDATE todos SET is_complete = 1, updated_by = ?, 
                         updated_at = CURRENT_TIMESTAMP WHERE task_id = ?''',
                      (updated_by, task_id))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success


class Permission:
    @staticmethod
    def grant(user_id, task_id):
        """Grant user access to a todo. Returns True if successful, False if already exists."""
        import sqlite3
        from database.db_setup import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO permissions (user_id, task_id) VALUES (?, ?)', 
                          (user_id, task_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Permission already exists
            return False
        finally:
            conn.close()
    
    @staticmethod
    def revoke(user_id, task_id):
        """Remove user access to a todo. Returns True if successful, False otherwise."""
        from database.db_setup import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM permissions WHERE user_id = ? AND task_id = ?', 
                      (user_id, task_id))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    @staticmethod
    def check(user_id, task_id):
        """Check if user can access this todo. Returns True if accessible, False otherwise."""
        from database.db_setup import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if user created the todo OR has explicit permission
        cursor.execute('''
            SELECT 1 FROM todos WHERE task_id = ? AND created_by = ?
            UNION
            SELECT 1 FROM permissions WHERE user_id = ? AND task_id = ?
        ''', (task_id, user_id, user_id, task_id))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    @staticmethod
    def get_user_todos(user_id):
        """Get all todos accessible to a user (created by them OR shared with them). Returns list of todo dicts."""
        from database.db_setup import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get todos created by user OR shared with user
        cursor.execute('''
            SELECT DISTINCT t.task_id, t.title, t.details, t.created_by, t.updated_by, 
                           t.created_at, t.updated_at, t.is_complete
            FROM todos t
            LEFT JOIN permissions p ON t.task_id = p.task_id
            WHERE t.created_by = ? OR p.user_id = ?
        ''', (user_id, user_id))
        
        rows = cursor.fetchall()
        conn.close()
        
        todos = []
        for row in rows:
            todos.append({
                'task_id': row[0],
                'title': row[1],
                'details': row[2],
                'created_by': row[3],
                'updated_by': row[4],
                'created_at': row[5],
                'updated_at': row[6],
                'is_complete': row[7]
            })
        return todos


class EncryptionKey:
    pass
