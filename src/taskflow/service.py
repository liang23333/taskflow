"""
Task service layer containing application business logic.
"""

from __future__ import annotations

from typing import Any

from taskflow.models import Priority, Status, Task
from taskflow.storage import TaskStorage


class TaskService:
    """Service layer coordinating task actions and storage."""

    def __init__(self, storage: TaskStorage):
        self.storage = storage

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: Priority = Priority.MEDIUM,
        tags: list[str] | None = None,
        project: str = "inbox",
        due_date: str | None = None,
    ) -> Task:
        """Create and persist a new task."""
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Task title cannot be empty")

        clean_tags = [t.strip().lower() for t in (tags or []) if t.strip()]

        task = Task(
            id=0,
            title=clean_title,
            description=description.strip(),
            status=Status.PENDING,
            priority=priority,
            tags=clean_tags,
            project=project.strip() or "inbox",
            due_date=due_date,
        )
        return self.storage.add(task)

    def get_task(self, task_id: int) -> Task | None:
        """Retrieve a task by ID."""
        return self.storage.get(task_id)

    def list_tasks(
        self,
        status: Status | None = None,
        priority: Priority | None = None,
        project: str | None = None,
        tag: str | None = None,
        search_query: str | None = None,
    ) -> list[Task]:
        """Query tasks with optional filters."""
        tasks = self.storage.list_all()

        if status:
            tasks = [t for t in tasks if t.status == status]
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        if project:
            tasks = [t for t in tasks if t.project.lower() == project.lower()]
        if tag:
            target_tag = tag.lower()
            tasks = [t for t in tasks if target_tag in [x.lower() for x in t.tags]]
        if search_query:
            query = search_query.lower()
            tasks = [
                t
                for t in tasks
                if query in t.title.lower() or query in t.description.lower()
            ]

        # Sort tasks: highest priority first, then ID
        tasks.sort(key=lambda t: (-t.priority.level, t.id))
        return tasks

    def mark_task_done(self, task_id: int) -> Task:
        """Mark a task as completed."""
        task = self.storage.get(task_id)
        if not task:
            raise KeyError(f"Task #{task_id} not found")
        task.mark_completed()
        return self.storage.update(task)

    def mark_task_in_progress(self, task_id: int) -> Task:
        """Mark a task as in progress."""
        task = self.storage.get(task_id)
        if not task:
            raise KeyError(f"Task #{task_id} not found")
        task.mark_in_progress()
        return self.storage.update(task)

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID."""
        return self.storage.delete(task_id)

    def get_summary(self) -> dict[str, Any]:
        """Generate statistical summary of tasks."""
        all_tasks = self.storage.list_all()
        total = len(all_tasks)
        pending = sum(1 for t in all_tasks if t.status == Status.PENDING)
        in_progress = sum(1 for t in all_tasks if t.status == Status.IN_PROGRESS)
        completed = sum(1 for t in all_tasks if t.status == Status.COMPLETED)
        cancelled = sum(1 for t in all_tasks if t.status == Status.CANCELLED)

        projects = set(t.project for t in all_tasks)
        tags = set(tag for t in all_tasks for tag in t.tags)

        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "cancelled": cancelled,
            "projects_count": len(projects),
            "tags_count": len(tags),
            "completion_rate": (completed / total * 100) if total > 0 else 0.0,
        }
