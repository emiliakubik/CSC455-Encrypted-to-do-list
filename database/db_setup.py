import sqlite3
import os

DATABASE_NAME = "todo_database.db"

def initialize_database():
    """Initialize the SQLite database with all required tables"""
    
    # Connect to database (creates file if it doesn't exist)
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # 1. Users table (user accounts so authorized users can contribute)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # 2. To do table (tasks)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            details TEXT,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_by INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_complete BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (created_by) REFERENCES users (user_id),
            FOREIGN KEY (updated_by) REFERENCES users (user_id)
        )
    ''')
    
    # 3. Permissions table (lists what tasks users are authorized to access/edit)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS permissions (
            permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (task_id) REFERENCES todos (task_id),
            UNIQUE(user_id, task_id)
        )
    ''')
    
    # 4. Encryption keys table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS encryption_keys (
            key_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task_id INTEGER NOT NULL,
            encrypted_key TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (task_id) REFERENCES todos (task_id),
            UNIQUE(user_id, task_id)
        )
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"Database '{DATABASE_NAME}' initialized successfully!")
    print("Created tables: users, todos, permissions, encryption_keys")

def get_connection():
    """Get a connection to the database"""
    return sqlite3.connect(DATABASE_NAME)

if __name__ == "__main__":
    # Run this file directly to initialize the database
    initialize_database()