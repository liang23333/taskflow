"""
Tests for Taskflow business logic service layer.
"""

import pytest

from taskflow.models import Priority, Status
from taskflow.service import TaskService


def test_create_task(task_service: TaskService) -> None:
    task = task_service.create_task(
        title="  Clean room  ",
        description="Make bed and dust shelves",
        priority=Priority.HIGH,
        tags=["home", "chore"],
        project="personal",
    )

    assert task.id == 1
    assert task.title == "Clean room"
    assert task.tags == ["home", "chore"]
    assert task.project == "personal"


def test_create_task_empty_title_raises(task_service: TaskService) -> None:
    with pytest.raises(ValueError, match="Task title cannot be empty"):
        task_service.create_task(title="   ")


def test_list_tasks_filtering(task_service: TaskService) -> None:
    task_service.create_task(
        title="Frontend bug", priority=Priority.LOW, project="web", tags=["ui"]
    )
    task_service.create_task(
        title="Backend bug", priority=Priority.URGENT, project="api", tags=["core"]
    )
    task_service.create_task(
        title="Documentation", priority=Priority.MEDIUM, project="web", tags=["docs"]
    )

    # Filter by project
    web_tasks = task_service.list_tasks(project="web")
    assert len(web_tasks) == 2

    # Filter by priority
    urgent_tasks = task_service.list_tasks(priority=Priority.URGENT)
    assert len(urgent_tasks) == 1
    assert urgent_tasks[0].title == "Backend bug"

    # Filter by tag
    ui_tasks = task_service.list_tasks(tag="ui")
    assert len(ui_tasks) == 1

    # Search keyword
    bug_tasks = task_service.list_tasks(search_query="bug")
    assert len(bug_tasks) == 2


def test_task_summary(task_service: TaskService) -> None:
    t1 = task_service.create_task(title="Task 1")
    task_service.create_task(title="Task 2")
    task_service.mark_task_done(t1.id)

    stats = task_service.get_summary()
    assert stats["total"] == 2
    assert stats["completed"] == 1
    assert stats["pending"] == 1
    assert stats["completion_rate"] == 50.0
