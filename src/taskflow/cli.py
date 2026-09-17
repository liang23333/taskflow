"""
Command-line interface (CLI) for Taskflow using argparse and Rich.
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from taskflow import __version__
from taskflow.config import get_default_json_path
from taskflow.models import Priority, Status
from taskflow.service import TaskService
from taskflow.storage import JsonTaskStorage

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None  # type: ignore


def print_message(text: str, style: str = "white") -> None:
    if RICH_AVAILABLE and console:
        console.print(f"[{style}]{text}[/{style}]")
    else:
        print(text)


def print_error(text: str) -> None:
    if RICH_AVAILABLE and console:
        console.print(f"[red bold]Error:[/red bold] [red]{text}[/red]")
    else:
        print(f"Error: {text}", file=sys.stderr)


def get_service() -> TaskService:
    storage = JsonTaskStorage(get_default_json_path())
    return TaskService(storage)


def cmd_add(args: argparse.Namespace) -> int:
    service = get_service()
    priority = Priority(args.priority)
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []

    task = service.create_task(
        title=args.title,
        description=args.description or "",
        priority=priority,
        tags=tags,
        project=args.project,
        due_date=args.due,
    )

    print_message(
        f"✓ Created task #{task.id}: '{task.title}' [{task.priority.value.upper()}] in '{task.project}'",
        style="green bold",
    )
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    service = get_service()
    status_filter = Status(args.status) if args.status else None
    priority_filter = Priority(args.priority) if args.priority else None

    tasks = service.list_tasks(
        status=status_filter,
        priority=priority_filter,
        project=args.project,
        tag=args.tag,
        search_query=args.search,
    )

    if not tasks:
        print_message("No tasks found matching your criteria.", style="yellow")
        return 0

    if RICH_AVAILABLE and console:
        table = Table(title="Taskflow Tasks", show_lines=False)
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Title", style="bold")
        table.add_column("Status", justify="center")
        table.add_column("Priority", justify="center")
        table.add_column("Project", style="magenta")
        table.add_column("Tags", style="dim")
        table.add_column("Due Date", justify="center", style="blue")

        status_colors = {
            Status.PENDING: "yellow",
            Status.IN_PROGRESS: "blue",
            Status.COMPLETED: "green",
            Status.CANCELLED: "dim",
        }

        for task in tasks:
            st_color = status_colors.get(task.status, "white")
            status_text = f"[{st_color}]{task.status.value}[/{st_color}]"
            priority_text = f"[{task.priority.color}]{task.priority.value.upper()}[/{task.priority.color}]"
            tags_text = ", ".join(task.tags) if task.tags else "-"
            due_text = task.due_date or "-"

            table.add_row(
                str(task.id),
                task.title,
                status_text,
                priority_text,
                task.project,
                tags_text,
                due_text,
            )

        console.print(table)
    else:
        for t in tasks:
            print(
                f"#{t.id:<3} [{t.status.value.upper():<11}] [{t.priority.value.upper():<6}] "
                f"[{t.project}] {t.title} {f'(Due: {t.due_date})' if t.due_date else ''}"
            )

    return 0


def cmd_done(args: argparse.Namespace) -> int:
    service = get_service()
    try:
        task = service.mark_task_done(args.task_id)
        print_message(
            f"✓ Task #{task.id} '{task.title}' marked as completed!",
            style="green bold",
        )
        return 0
    except KeyError as e:
        print_error(str(e))
        return 1


def cmd_delete(args: argparse.Namespace) -> int:
    service = get_service()
    if service.delete_task(args.task_id):
        print_message(f"✓ Task #{args.task_id} deleted.", style="green")
        return 0
    else:
        print_error(f"Task #{args.task_id} not found.")
        return 1


def cmd_summary(_args: argparse.Namespace) -> int:
    service = get_service()
    stats = service.get_summary()

    if RICH_AVAILABLE and console:
        panel_content = (
            f"[bold]Total Tasks:[/bold] {stats['total']}\n"
            f"[yellow]Pending:[/yellow] {stats['pending']}  |  "
            f"[blue]In Progress:[/blue] {stats['in_progress']}  |  "
            f"[green]Completed:[/green] {stats['completed']}  |  "
            f"[dim]Cancelled:[/dim] {stats['cancelled']}\n"
            f"[magenta]Projects:[/magenta] {stats['projects_count']}  |  "
            f"[cyan]Tags:[/cyan] {stats['tags_count']}\n"
            f"[bold green]Completion Rate:[/bold green] {stats['completion_rate']:.1f}%"
        )
        console.print(Panel(panel_content, title="Taskflow Summary", expand=False))
    else:
        print("Taskflow Summary:")
        print(f"  Total Tasks: {stats['total']}")
        print(f"  Pending: {stats['pending']}")
        print(f"  In Progress: {stats['in_progress']}")
        print(f"  Completed: {stats['completed']}")
        print(f"  Completion Rate: {stats['completion_rate']:.1f}%")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="taskflow",
        description="Taskflow - Modern Python Task Management Application",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # add
    parser_add = subparsers.add_parser("add", help="Add a new task")
    parser_add.add_argument("title", help="Task title")
    parser_add.add_argument("-d", "--description", help="Detailed description")
    parser_add.add_argument(
        "-p",
        "--priority",
        choices=["low", "medium", "high", "urgent"],
        default="medium",
        help="Task priority level (default: medium)",
    )
    parser_add.add_argument(
        "-g", "--tags", help="Comma-separated tags (e.g. 'work,urgent')"
    )
    parser_add.add_argument(
        "--project", default="inbox", help="Project / category (default: inbox)"
    )
    parser_add.add_argument("--due", help="Due date (YYYY-MM-DD)")
    parser_add.set_defaults(func=cmd_add)

    # list
    parser_list = subparsers.add_parser("list", help="List and filter tasks")
    parser_list.add_argument(
        "-s",
        "--status",
        choices=["pending", "in_progress", "completed", "cancelled"],
        help="Filter by status",
    )
    parser_list.add_argument(
        "-p",
        "--priority",
        choices=["low", "medium", "high", "urgent"],
        help="Filter by priority",
    )
    parser_list.add_argument("--project", help="Filter by project")
    parser_list.add_argument("-t", "--tag", help="Filter by tag")
    parser_list.add_argument("-q", "--search", help="Search keywords in title/desc")
    parser_list.set_defaults(func=cmd_list)

    # done
    parser_done = subparsers.add_parser("done", help="Mark a task as completed")
    parser_done.add_argument("task_id", type=int, help="ID of task to complete")
    parser_done.set_defaults(func=cmd_done)

    # delete
    parser_del = subparsers.add_parser("delete", help="Delete a task")
    parser_del.add_argument("task_id", type=int, help="ID of task to delete")
    parser_del.set_defaults(func=cmd_delete)

    # summary
    parser_sum = subparsers.add_parser("summary", help="Show task statistics summary")
    parser_sum.set_defaults(func=cmd_summary)

    return parser


def main(args: Sequence[str] | None = None) -> int:
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 0

    return parsed_args.func(parsed_args)


if __name__ == "__main__":
    sys.exit(main())
