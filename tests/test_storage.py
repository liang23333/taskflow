"""
Tests for Taskflow storage implementations (JSON and SQLite).
"""

import pytest

from taskflow.models import Priority, Status, Task
from taskflow.storage import JsonTaskStorage, SQLiteTaskStorage


@pytest.mark.parametrize("storage_fixture", ["json_storage", "sqlite_storage"])
def test_storage_crud(storage_fixture: str, request: pytest.FixtureRequest) -> None:
    storage = request.getfixturevalue(storage_fixture)

    # Initial state
    assert len(storage.list_all()) == 0

    # Add task
    task = Task(
        id=0,
        title="Persist me",
        description="Storage test",
        priority=Priority.HIGH,
        tags=["db"],
        project="infra",
    )
    saved_task = storage.add(task)
    assert saved_task.id > 0
    assert len(storage.list_all()) == 1

    # Get task
    retrieved = storage.get(saved_task.id)
    assert retrieved is not None
    assert retrieved.title == "Persist me"
    assert retrieved.priority == Priority.HIGH
    assert retrieved.tags == ["db"]

    # Update task
    retrieved.mark_completed()
    retrieved.title = "Updated title"
    updated = storage.update(retrieved)
    assert updated.status == Status.COMPLETED
    assert updated.title == "Updated title"

    # Verify update in fresh fetch
    fresh = storage.get(saved_task.id)
    assert fresh is not None
    assert fresh.status == Status.COMPLETED
    assert fresh.title == "Updated title"

    # Delete task
    assert storage.delete(saved_task.id) is True
    assert storage.get(saved_task.id) is None
    assert len(storage.list_all()) == 0
