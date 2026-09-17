"""
Domain models for Taskflow.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

    @property
    def level(self) -> int:
        levels = {
            Priority.LOW: 1,
            Priority.MEDIUM: 2,
            Priority.HIGH: 3,
            Priority.URGENT: 4,
        }
        return levels[self]

    @property
    def color(self) -> str:
        colors = {
            Priority.LOW: "cyan",
            Priority.MEDIUM: "blue",
            Priority.HIGH: "yellow",
            Priority.URGENT: "red bold",
        }
        return colors[self]


class Status(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    status: Status = Status.PENDING
    priority: Priority = Priority.MEDIUM
    tags: list[str] = field(default_factory=list)
    project: str = "inbox"
    due_date: str | None = None  # Format: YYYY-MM-DD or ISO 8601
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    completed_at: str | None = None

    def mark_completed(self) -> None:
        """Mark the task as completed."""
        self.status = Status.COMPLETED
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.touch()

    def mark_in_progress(self) -> None:
        """Mark the task as in progress."""
        self.status = Status.IN_PROGRESS
        self.completed_at = None
        self.touch()

    def mark_pending(self) -> None:
        """Reset task status to pending."""
        self.status = Status.PENDING
        self.completed_at = None
        self.touch()

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Convert task instance to dictionary."""
        data = asdict(self)
        data["status"] = self.status.value
        data["priority"] = self.priority.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        """Construct a Task instance from dictionary."""
        return cls(
            id=int(data["id"]),
            title=data["title"],
            description=data.get("description", ""),
            status=Status(data.get("status", Status.PENDING.value)),
            priority=Priority(data.get("priority", Priority.MEDIUM.value)),
            tags=list(data.get("tags", [])),
            project=data.get("project", "inbox"),
            due_date=data.get("due_date"),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
            completed_at=data.get("completed_at"),
        )
