#!/usr/bin/env python3
"""Simple car counter app — track cars per location stored in a JSON file."""

import argparse
import json
import os
import sys

DEFAULT_DB = os.path.expanduser("~/.car_counter.json")


def load(db: str) -> dict:
    if os.path.exists(db):
        with open(db) as f:
            return json.load(f)
    return {}


def save(db: str, data: dict) -> None:
    with open(db, "w") as f:
        json.dump(data, f, indent=2)


def cmd_add(args, data: dict) -> None:
    location = args.location
    count = args.count
    data[location] = data.get(location, 0) + count
    print(f"Added {count} car(s) at '{location}'. Total: {data[location]}")


def cmd_list(args, data: dict) -> None:
    if not data:
        print("No cars counted yet.")
        return
    width = max(len(loc) for loc in data)
    print(f"{'Location':<{width}}  Count")
    print("-" * (width + 8))
    for location, count in sorted(data.items()):
        print(f"{location:<{width}}  {count}")


def cmd_reset(args, data: dict) -> None:
    location = args.location
    if location:
        if location in data:
            data[location] = 0
            print(f"Reset count for '{location}'.")
        else:
            print(f"Location '{location}' not found.")
    else:
        data.clear()
        print("All counts reset.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple car counter app")
    parser.add_argument("--db", default=DEFAULT_DB, help="Path to JSON database file")
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="Add cars at a location")
    p_add.add_argument("location", help="Location name")
    p_add.add_argument("count", nargs="?", type=int, default=1, help="Number of cars (default: 1)")

    sub.add_parser("list", help="List all counted cars")

    p_reset = sub.add_parser("reset", help="Reset count for a location or all locations")
    p_reset.add_argument("location", nargs="?", help="Location to reset (omit to reset all)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    data = load(args.db)

    if args.command == "add":
        cmd_add(args, data)
    elif args.command == "list":
        cmd_list(args, data)
    elif args.command == "reset":
        cmd_reset(args, data)

    save(args.db, data)


if __name__ == "__main__":
    main()
