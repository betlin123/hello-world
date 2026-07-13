#!/usr/bin/env python3
"""A simple command-line to-do app."""

import argparse
import json
import sys
from pathlib import Path

DEFAULT_DB_PATH = Path.home() / ".todo.json"


def load_tasks(db_path: Path) -> list[dict]:
    if not db_path.exists():
        return []
    with db_path.open("r") as f:
        return json.load(f)


def save_tasks(db_path: Path, tasks: list[dict]) -> None:
    with db_path.open("w") as f:
        json.dump(tasks, f, indent=2)


def add_task(db_path: Path, text: str) -> None:
    tasks = load_tasks(db_path)
    task_id = max((t["id"] for t in tasks), default=0) + 1
    tasks.append({"id": task_id, "text": text, "done": False})
    save_tasks(db_path, tasks)
    print(f"Added task {task_id}: {text}")


def list_tasks(db_path: Path) -> None:
    tasks = load_tasks(db_path)
    if not tasks:
        print("No tasks yet.")
        return
    for task in tasks:
        status = "x" if task["done"] else " "
        print(f"[{status}] {task['id']}: {task['text']}")


def complete_task(db_path: Path, task_id: int) -> None:
    tasks = load_tasks(db_path)
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            save_tasks(db_path, tasks)
            print(f"Completed task {task_id}: {task['text']}")
            return
    print(f"No task found with id {task_id}")
    sys.exit(1)


def delete_task(db_path: Path, task_id: int) -> None:
    tasks = load_tasks(db_path)
    remaining = [t for t in tasks if t["id"] != task_id]
    if len(remaining) == len(tasks):
        print(f"No task found with id {task_id}")
        sys.exit(1)
    save_tasks(db_path, remaining)
    print(f"Deleted task {task_id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="A simple to-do list manager.")
    parser.add_argument(
        "--db", type=Path, default=DEFAULT_DB_PATH, help="Path to the tasks database file."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new task.")
    add_parser.add_argument("text", help="Description of the task.")

    subparsers.add_parser("list", help="List all tasks.")

    complete_parser = subparsers.add_parser("complete", help="Mark a task as done.")
    complete_parser.add_argument("id", type=int, help="ID of the task to complete.")

    delete_parser = subparsers.add_parser("delete", help="Delete a task.")
    delete_parser.add_argument("id", type=int, help="ID of the task to delete.")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "add":
        add_task(args.db, args.text)
    elif args.command == "list":
        list_tasks(args.db)
    elif args.command == "complete":
        complete_task(args.db, args.id)
    elif args.command == "delete":
        delete_task(args.db, args.id)


if __name__ == "__main__":
    main()
