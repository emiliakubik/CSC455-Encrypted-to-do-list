"""
Encrypted task manager.

All todo details are stored encrypted using a symmetric data key unique to each
task. Whenever the task is shared with another collaborator the same data key is
encrypted for that user and stored in the encryption_keys table. This enables
multiple users to decrypt the exact same todo payload while ensuring the data is
protected at rest in the database.
"""

from __future__ import annotations

import sqlite3
from typing import Iterable, List, Optional, Sequence, Tuple

from crypto import encryption, key_manager
from database.db_setup import get_connection


def create_encrypted_task(
    title: str,
    details: Optional[str],
    created_by: int,
    shared_with: Optional[Iterable[int]] = None,
) -> Tuple[bool, str, Optional[int]]:
    """
    Create a task whose details are encrypted at rest.
    shared_with should contain user IDs that also need access (owner always included).
    """
    title = (title or "").strip()
    if not title:
        return False, "Title is required", None
    
    normalized_shared = _normalize_shared_users(shared_with)
    
    data_key = encryption.generate_data_key()
    encrypted_details = encryption.encrypt_message(details, data_key)
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO todos (title, details, created_by, updated_by)
            VALUES (?, ?, ?, ?)
            """,
            (title, encrypted_details, created_by, created_by),
        )
        task_id = cursor.lastrowid
        _grant_user_access(cursor, created_by, task_id, data_key)
        for user_id in normalized_shared:
            if user_id == created_by:
                continue
            _grant_user_access(cursor, user_id, task_id, data_key)
        conn.commit()
        return True, "Task created", task_id
    finally:
        conn.close()


def get_tasks_for_user(user_id: int) -> List[dict]:
    """Return decrypted todos the user is authorized to access."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT t.task_id, t.title, t.details, t.created_by, t.updated_by,
               t.created_at, t.updated_at, t.is_complete, ek.encrypted_key
        FROM todos t
        JOIN permissions p ON p.task_id = t.task_id
        JOIN encryption_keys ek
             ON ek.task_id = t.task_id AND ek.user_id = p.user_id
        WHERE p.user_id = ?
        ORDER BY t.created_at ASC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    
    todos = []
    for row in rows:
        data_key = key_manager.decrypt_data_key_for_user(user_id, row["encrypted_key"])
        decrypted_details = encryption.decrypt_message(row["details"], data_key)
        todos.append(
            {
                "task_id": row["task_id"],
                "title": row["title"],
                "details": decrypted_details,
                "created_by": row["created_by"],
                "updated_by": row["updated_by"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "is_complete": bool(row["is_complete"]),
            }
        )
    return todos


def share_task_with_user(task_id: int, owner_id: int, target_user_id: int) -> Tuple[bool, str]:
    """
    Share an existing task with another user by copying the data key for them.
    owner_id must already have access to the task.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        data_key = _get_data_key_for_user(cursor, owner_id, task_id)
        if data_key is None:
            return False, "Owner does not have access to this task"
        
        _grant_user_access(cursor, target_user_id, task_id, data_key)
        conn.commit()
        return True, "Task shared"
    finally:
        conn.close()


def update_task(
    task_id: int,
    user_id: int,
    *,
    new_title: Optional[str] = None,
    new_details: Optional[str] = None,
    is_complete: Optional[bool] = None,
) -> Tuple[bool, str]:
    """Update an encrypted todo. Caller must already have access."""
    if new_title is None and new_details is None and is_complete is None:
        return False, "No updates provided"
    
    updates = []
    params: List[object] = []
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        data_key = _get_data_key_for_user(cursor, user_id, task_id)
        if data_key is None:
            return False, "User does not have access to this task"
        
        if new_title is not None:
            title = new_title.strip()
            if not title:
                return False, "Title cannot be empty"
            updates.append("title = ?")
            params.append(title)
        
        if new_details is not None:
            encrypted_details = encryption.encrypt_message(new_details, data_key)
            updates.append("details = ?")
            params.append(encrypted_details)
        
        if is_complete is not None:
            updates.append("is_complete = ?")
            params.append(1 if is_complete else 0)
        
        if not updates:
            return False, "No updates provided"
        
        updates.append("updated_by = ?")
        params.append(user_id)
        set_clause = ", ".join(updates + ["updated_at = CURRENT_TIMESTAMP"])
        cursor.execute(
            f"UPDATE todos SET {set_clause} WHERE task_id = ?",
            (*params, task_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return False, "Task not found"
        return True, "Task updated"
    finally:
        conn.close()


def read_task(task_id: int, user_id: int) -> Optional[dict]:
    """Fetch and decrypt a single todo for the specified user."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT t.*, ek.encrypted_key
        FROM todos t
        JOIN permissions p ON p.task_id = t.task_id
        JOIN encryption_keys ek
             ON ek.task_id = t.task_id AND ek.user_id = p.user_id
        WHERE t.task_id = ? AND p.user_id = ?
        """,
        (task_id, user_id),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    
    data_key = key_manager.decrypt_data_key_for_user(user_id, row["encrypted_key"])
    decrypted_details = encryption.decrypt_message(row["details"], data_key)
    return {
        "task_id": row["task_id"],
        "title": row["title"],
        "details": decrypted_details,
        "created_by": row["created_by"],
        "updated_by": row["updated_by"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "is_complete": bool(row["is_complete"]),
    }


def _normalize_shared_users(shared_with: Optional[Iterable[int]]) -> Sequence[int]:
    if not shared_with:
        return []
    unique_ids = []
    seen = set()
    for user_id in shared_with:
        if user_id is None:
            continue
        normalized = int(user_id)
        if normalized in seen:
            continue
        seen.add(normalized)
        unique_ids.append(normalized)
    return unique_ids


def _grant_user_access(cursor: sqlite3.Cursor, user_id: int, task_id: int, data_key: bytes) -> None:
    cursor.execute(
        "INSERT OR IGNORE INTO permissions (user_id, task_id) VALUES (?, ?)",
        (user_id, task_id),
    )
    encrypted_key = key_manager.encrypt_data_key_for_user(user_id, data_key)
    cursor.execute(
        """
        INSERT INTO encryption_keys (user_id, task_id, encrypted_key)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, task_id) DO UPDATE SET encrypted_key = excluded.encrypted_key
        """,
        (user_id, task_id, encrypted_key),
    )


def _get_data_key_for_user(cursor: sqlite3.Cursor, user_id: int, task_id: int) -> Optional[bytes]:
    cursor.execute(
        "SELECT encrypted_key FROM encryption_keys WHERE user_id = ? AND task_id = ?",
        (user_id, task_id),
    )
    row = cursor.fetchone()
    if not row:
        return None
    return key_manager.decrypt_data_key_for_user(user_id, row[0])
