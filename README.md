# Taskflow 📋

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Architecture: src-layout](https://img.shields.io/badge/layout-src--layout-orange.svg)](https://packaging.python.org/)

A modern, fast, and extensible Python task management application and workflow engine. Designed for developers and terminal power users who want friction-free productivity tracking, clean domain separation, and modular storage backends.

---

## ✨ Features

- **🚀 Dual Storage Backends**: Zero-configuration JSON file storage or SQLite persistence with pluggable storage interfaces.
- **🏷️ Flexible Metadata**: Tasks support statuses (`pending`, `in_progress`, `completed`, `cancelled`), priorities (`low`, `medium`, `high`, `urgent`), projects/categories, due dates, and tags.
- **💻 Rich Terminal Interface**: Beautiful command-line experience powered by [Rich](https://github.com/Textualize/rich) with tables, colored priority indicators, and progress bars.
- **🧱 Clean Architecture**: Separation of domain models, storage adapters, service layer, and CLI interfaces.
- **🧪 Production-Ready Tooling**: Modern packaging with `pyproject.toml` (PEP 621), `src/` layout, unit tests with `pytest`, linting and formatting with `ruff`, and strict type hints with `mypy`.

---

## 📂 Project Structure

This repository follows modern Python packaging best practices using the **`src/` layout**:

```text
taskflow/
├── .github/                     # CI/CD workflows and issue templates
│   └── workflows/
│       └── ci.yml               # Automated linting and tests
├── src/
│   └── taskflow/                # Application source code
│       ├── __init__.py          # Package exports & version
│       ├── cli.py               # Terminal CLI commands & Rich UI
│       ├── config.py            # Path resolution & defaults
│       ├── models.py            # Task, Priority, Status domain models
│       ├── service.py           # Task management business logic
│       └── storage.py           # JSON and SQLite persistence adapters
├── tests/                       # Unit and integration test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures and temporary storage
│   ├── test_cli.py              # CLI entry point tests
│   ├── test_models.py           # Domain model tests
│   ├── test_service.py          # Business logic tests
│   └── test_storage.py          # Storage backend tests
├── .gitignore                   # Standard Python .gitignore
├── LICENSE                      # MIT License
├── pyproject.toml               # Build configuration (PEP 621 / Hatchling)
└── README.md                    # Project documentation
```

### Why the `src/` Layout?
- **Prevents Accidental Imports**: Avoids importing the local uninstalled directory during tests, ensuring you test the exact installed package.
- **Clean Packaging**: Guarantees that only files intended for distribution under `src/taskflow` get packaged into wheel and sdist distributions.
- **Tool Compatibility**: Out-of-the-box compatibility with `hatchling`, `flit`, `poetry`, and `setuptools`.

---

## ⚡ Quick Start

### 1. Installation

Clone the repository and install it in editable mode:

```bash
# Clone repository
git clone https://github.com/liang23333/taskflow.git
cd taskflow

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install editable package with development dependencies
pip install -e ".[dev]"
```

*(Alternatively, if you use [uv](https://github.com/astral-sh/uv): `uv pip install -e ".[dev]" `)*

### 2. Usage Examples

```bash
# Add a new task
taskflow add "Implement SQLite storage layer" -p high -g backend,db --project core --due 2026-04-01

# List all open tasks in a rich table
taskflow list

# Filter tasks by priority or project
taskflow list --priority high --project core

# Mark a task as completed
taskflow done 1

# View task metrics and summary
taskflow summary

# Delete a task
taskflow delete 1
```

---

## 🛠️ Development & Quality Assurance

### Run Tests
```bash
# Run pytest with coverage report
pytest
```

### Linting and Formatting (Ruff)
```bash
# Check code with Ruff
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Format code
ruff format .
```

### Type Checking (Mypy)
```bash
mypy src/taskflow
```

---

## 🗺️ Roadmap & Milestones

- [x] **Milestone 1**: Project scaffolding, `src/` layout, models, JSON storage, and CLI basics.
- [ ] **Milestone 2**: SQLite persistence adapter with transactions and schema migrations.
- [ ] **Milestone 3**: Advanced querying, fuzzy search, full-text search, and multi-field sorting.
- [ ] **Milestone 4**: Interactive Terminal UI (TUI) powered by Textual.
- [ ] **Milestone 5**: Data import/export (`todo.txt`, JSON, Markdown, CSV).
- [ ] **Milestone 6**: REST API / MCP (Model Context Protocol) server integration.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
