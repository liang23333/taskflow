"""
Tests for Taskflow domain models.
"""

from taskflow.models import Priority, Status, Task


def test_task_creation() -> None:
    task = Task(id=1, title="Write unit tests")
    assert task.id == 1
    assert task.title == "Write unit tests"
    assert task.status == Status.PENDING
    assert task.priority == Priority.MEDIUM
    assert task.project == "inbox"
    assert task.tags == []
    assert task.completed_at is None


def test_task_status_transitions() -> None:
    task = Task(id=1, title="Test transitions")

    task.mark_in_progress()
    assert task.status == Status.IN_PROGRESS
    assert task.completed_at is None

    task.mark_completed()
    assert task.status == Status.COMPLETED
    assert task.completed_at is not None

    task.mark_pending()
    assert task.status == Status.PENDING
    assert task.completed_at is None


def test_task_serialization() -> None:
    task = Task(
        id=42,
        title="Serialize me",
        description="Detailed description",
        priority=Priority.URGENT,
        tags=["alpha", "beta"],
        project="core",
        due_date="2026-05-01",
    )

    data = task.to_dict()
    assert data["id"] == 42
    assert data["priority"] == "urgent"
    assert data["status"] == "pending"
    assert data["tags"] == ["alpha", "beta"]

    restored = Task.from_dict(data)
    assert restored.id == task.id
    assert restored.title == task.title
    assert restored.priority == Priority.URGENT
    assert restored.status == Status.PENDING
    assert restored.tags == ["alpha", "beta"]
