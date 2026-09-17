"""
Storage layer providing abstract interface, JSON storage, and SQLite storage.
"""

from __future__ import annotations

import json
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path

from taskflow.models import Priority, Status, Task


class TaskStorage(ABC):
    """Abstract base class defining storage operations."""

    @abstractmethod
    def list_all(self) -> list[Task]:
        """Retrieve all stored tasks."""
        pass

    @abstractmethod
    def get(self, task_id: int) -> Task | None:
        """Retrieve a task by ID."""
        pass

    @abstractmethod
    def add(self, task: Task) -> Task:
        """Add a new task and assign its ID."""
        pass

    @abstractmethod
    def update(self, task: Task) -> Task:
        """Update an existing task."""
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Delete a task by ID. Returns True if deleted."""
        pass

    @abstractmethod
    def next_id(self) -> int:
        """Generate the next auto-incrementing ID."""
        pass


class JsonTaskStorage(TaskStorage):
    """File-based JSON storage implementation."""

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self._ensure_file()

    def _ensure_file(self) -> None:
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_raw([])

    def _load_raw(self) -> list[dict]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_raw(self, data: list[dict]) -> None:
        temp_file = self.file_path.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_file.replace(self.file_path)

    def list_all(self) -> list[Task]:
        raw_items = self._load_raw()
        return [Task.from_dict(item) for item in raw_items]

    def get(self, task_id: int) -> Task | None:
        for task in self.list_all():
            if task.id == task_id:
                return task
        return None

    def next_id(self) -> int:
        tasks = self.list_all()
        if not tasks:
            return 1
        return max(t.id for t in tasks) + 1

    def add(self, task: Task) -> Task:
        tasks = self.list_all()
        if task.id <= 0:
            task.id = self.next_id()
        tasks.append(task)
        self._save_raw([t.to_dict() for t in tasks])
        return task

    def update(self, task: Task) -> Task:
        tasks = self.list_all()
        found = False
        task.touch()
        for idx, t in enumerate(tasks):
            if t.id == task.id:
                tasks[idx] = task
                found = True
                break
        if not found:
            raise KeyError(f"Task with ID {task.id} not found")
        self._save_raw([t.to_dict() for t in tasks])
        return task

    def delete(self, task_id: int) -> bool:
        tasks = self.list_all()
        initial_len = len(tasks)
        tasks = [t for t in tasks if t.id != task_id]
        if len(tasks) < initial_len:
            self._save_raw([t.to_dict() for t in tasks])
            return True
        return False


class SQLiteTaskStorage(TaskStorage):
    """SQLite-backed persistent storage implementation."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    project TEXT NOT NULL,
                    due_date TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT
                )
                """
            )
            conn.commit()

    def list_all(self) -> list[Task]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM tasks ORDER BY id ASC")
            rows = cursor.fetchall()
            return [
                Task(
                    id=row["id"],
                    title=row["title"],
                    description=row["description"] or "",
                    status=Status(row["status"]),
                    priority=Priority(row["priority"]),
                    tags=json.loads(row["tags"]) if row["tags"] else [],
                    project=row["project"],
                    due_date=row["due_date"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    completed_at=row["completed_at"],
                )
                for row in rows
            ]

    def get(self, task_id: int) -> Task | None:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return Task(
                id=row["id"],
                title=row["title"],
                description=row["description"] or "",
                status=Status(row["status"]),
                priority=Priority(row["priority"]),
                tags=json.loads(row["tags"]) if row["tags"] else [],
                project=row["project"],
                due_date=row["due_date"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                completed_at=row["completed_at"],
            )

    def next_id(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT MAX(id) FROM tasks")
            row = cursor.fetchone()
            max_id = row[0] if row and row[0] is not None else 0
            return max_id + 1

    def add(self, task: Task) -> Task:
        with self._get_connection() as conn:
            tags_json = json.dumps(task.tags)
            cursor = conn.execute(
                """
                INSERT INTO tasks (
                    title, description, status, priority, tags, project, due_date, created_at, updated_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.title,
                    task.description,
                    task.status.value,
                    task.priority.value,
                    tags_json,
                    task.project,
                    task.due_date,
                    task.created_at,
                    task.updated_at,
                    task.completed_at,
                ),
            )
            conn.commit()
            task.id = cursor.lastrowid or self.next_id()
            return task

    def update(self, task: Task) -> Task:
        task.touch()
        with self._get_connection() as conn:
            tags_json = json.dumps(task.tags)
            cursor = conn.execute(
                """
                UPDATE tasks SET
                    title = ?,
                    description = ?,
                    status = ?,
                    priority = ?,
                    tags = ?,
                    project = ?,
                    due_date = ?,
                    updated_at = ?,
                    completed_at = ?
                WHERE id = ?
                """,
                (
                    task.title,
                    task.description,
                    task.status.value,
                    task.priority.value,
                    tags_json,
                    task.project,
                    task.due_date,
                    task.updated_at,
                    task.completed_at,
                    task.id,
                ),
            )
            conn.commit()
            if cursor.rowcount == 0:
                raise KeyError(f"Task with ID {task.id} not found")
            return task

    def delete(self, task_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0
