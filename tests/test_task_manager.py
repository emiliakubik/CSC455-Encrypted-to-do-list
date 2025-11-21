import pytest

from core import task_manager
from crypto import key_manager
from database import db_setup
from database.models import User


@pytest.fixture(autouse=True)
def temp_environment(tmp_path, monkeypatch):
    """Isolate the SQLite DB and master key for every test run."""
    db_path = tmp_path / "todo.db"
    monkeypatch.setattr(db_setup, "DATABASE_NAME", str(db_path))
    db_setup.initialize_database()
    
    key_path = tmp_path / "master.key"
    monkeypatch.setenv(key_manager.MASTER_KEY_ENV_VAR, str(key_path))
    key_manager.reset_master_key_cache()
    yield


def test_create_task_encrypts_details_and_returns_plaintext_for_owner():
    owner_id = User.create("owner", "pw")
    success, _, task_id = task_manager.create_encrypted_task("Secret", "Hidden notes", owner_id)
    assert success is True
    assert task_id is not None
    
    # Details are encrypted at rest.
    conn = db_setup.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT details FROM todos WHERE task_id = ?", (task_id,))
    stored_details = cursor.fetchone()[0]
    conn.close()
    assert "Hidden notes" not in stored_details
    
    tasks = task_manager.get_tasks_for_user(owner_id)
    assert len(tasks) == 1
    assert tasks[0]["details"] == "Hidden notes"


def test_share_task_grants_access_to_collaborator():
    owner_id = User.create("owner", "pw")
    collaborator_id = User.create("collab", "pw")
    success, _, task_id = task_manager.create_encrypted_task("Joint task", "Classified", owner_id)
    assert success is True
    
    share_success, _ = task_manager.share_task_with_user(task_id, owner_id, collaborator_id)
    assert share_success is True
    
    collaborator_tasks = task_manager.get_tasks_for_user(collaborator_id)
    assert collaborator_tasks and collaborator_tasks[0]["details"] == "Classified"


def test_update_task_reencrypts_payload_for_all_users():
    owner_id = User.create("owner", "pw")
    collaborator_id = User.create("collab", "pw")
    success, _, task_id = task_manager.create_encrypted_task(
        "Joint task",
        "Old value",
        owner_id,
        shared_with=[collaborator_id],
    )
    assert success is True
    
    # Collaborator updates the task details.
    updated, _ = task_manager.update_task(
        task_id,
        collaborator_id,
        new_details="New shared value",
    )
    assert updated is True
    
    tasks_owner = task_manager.get_tasks_for_user(owner_id)
    assert tasks_owner[0]["details"] == "New shared value"
    
    tasks_collab = task_manager.get_tasks_for_user(collaborator_id)
    assert tasks_collab[0]["details"] == "New shared value"
