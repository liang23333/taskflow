"""
Configuration and default directory resolution for Taskflow.
"""

from __future__ import annotations

import os
from pathlib import Path


def get_data_dir() -> Path:
    """
    Get the application data directory adhering to XDG standards or user home.
    """
    xdg_data = os.getenv("XDG_DATA_HOME")
    if xdg_data:
        base_dir = Path(xdg_data) / "taskflow"
    else:
        base_dir = Path.home() / ".taskflow"

    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def get_default_json_path() -> Path:
    """Get the default JSON storage file path."""
    return get_data_dir() / "tasks.json"


def get_default_sqlite_path() -> Path:
    """Get the default SQLite storage file path."""
    return get_data_dir() / "tasks.db"
