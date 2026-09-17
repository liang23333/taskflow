"""
Pytest configuration and shared fixtures for Taskflow tests.
"""

import tempfile
from pathlib import Path

import pytest

from taskflow.models import Priority, Status, Task
from taskflow.service import TaskService
from taskflow.storage import JsonTaskStorage, SQLiteTaskStorage


@pytest.fixture
def temp_json_path(tmp_path: Path) -> Path:
    return tmp_path / "test_tasks.json"


@pytest.fixture
def temp_sqlite_path(tmp_path: Path) -> Path:
    return tmp_path / "test_tasks.db"


@pytest.fixture
def json_storage(temp_json_path: Path) -> JsonTaskStorage:
    return JsonTaskStorage(temp_json_path)


@pytest.fixture
def sqlite_storage(temp_sqlite_path: Path) -> SQLiteTaskStorage:
    return SQLiteTaskStorage(temp_sqlite_path)


@pytest.fixture
def task_service(json_storage: JsonTaskStorage) -> TaskService:
    return TaskService(json_storage)


@pytest.fixture
def sample_task() -> Task:
    return Task(
        id=1,
        title="Test Task",
        description="Test Description",
        status=Status.PENDING,
        priority=Priority.HIGH,
        tags=["test", "qa"],
        project="backend",
        due_date="2026-12-31",
    )
