"""
Tests for Taskflow command line interface.
"""

from taskflow.cli import build_parser


def test_cli_parser_add() -> None:
    parser = build_parser()
    args = parser.parse_args(
        ["add", "Buy groceries", "-p", "high", "-g", "errands,home", "--project", "life"]
    )
    assert args.command == "add"
    assert args.title == "Buy groceries"
    assert args.priority == "high"
    assert args.tags == "errands,home"
    assert args.project == "life"


def test_cli_parser_list() -> None:
    parser = build_parser()
    args = parser.parse_args(["list", "-s", "pending", "-p", "urgent", "--project", "work"])
    assert args.command == "list"
    assert args.status == "pending"
    assert args.priority == "urgent"
    assert args.project == "work"


def test_cli_parser_done() -> None:
    parser = build_parser()
    args = parser.parse_args(["done", "42"])
    assert args.command == "done"
    assert args.task_id == 42


def test_cli_parser_delete() -> None:
    parser = build_parser()
    args = parser.parse_args(["delete", "7"])
    assert args.command == "delete"
    assert args.task_id == 7
