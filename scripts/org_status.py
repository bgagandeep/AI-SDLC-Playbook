#!/usr/bin/env python3
"""Agent org state machine and review queue tracker."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

STATUS_FILE = Path("reviews/agent_org_status.json")

ROLES = (
    "CEO",
    "CTO",
    "ProductManager",
    "Architect",
    "Planner",
    "Worker",
    "QA_Eval",
    "AdversarialReviewer",
    "ReleaseGate",
    "SRE_Ops",
)
HUMAN_ROLES = ("CEO",)
STATES = ("idle", "busy", "blocked", "awaiting_human")


def default_status() -> dict[str, Any]:
    return {
        "roster": {
            role: {
                "type": "human" if role in HUMAN_ROLES else "agent",
                "status": "idle",
                "active_task": None,
            }
            for role in ROLES
        },
        "review_queue": [],
    }


def load_status() -> dict[str, Any]:
    if not STATUS_FILE.exists():
        return default_status()
    try:
        data = json.loads(STATUS_FILE.read_text())
    except json.JSONDecodeError:
        return default_status()

    merged = default_status()
    for role, info in data.get("roster", {}).items():
        if role in merged["roster"] and isinstance(info, dict):
            merged["roster"][role].update(
                {k: v for k, v in info.items() if k in ("type", "status", "active_task")}
            )
    merged["review_queue"] = data.get("review_queue", [])
    return merged


def save_status(data: dict[str, Any]) -> None:
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(data, indent=2) + "\n")


def cmd_show(args: argparse.Namespace) -> int:
    data = load_status()
    if args.json:
        print(json.dumps(data, indent=2))
        return 0

    print("\n--- 10-Agent Software Factory Status ---")
    for role, info in data["roster"].items():
        print(
            f"  - {role:<20} [{info['type']:<5}] status: {info['status']:<14} "
            f"task: {info['active_task'] or 'None'}"
        )
    queue = data["review_queue"]
    print(f"\nActive review queue items: {len(queue)}")
    for item in queue:
        print(
            f"  - [{item.get('pr_id', 'N/A')}] {item.get('title', 'Untitled')} "
            f"(assignee: {item.get('assignee', 'Unassigned')})"
        )
    print("----------------------------------------\n")
    return 0


def cmd_set(args: argparse.Namespace) -> int:
    data = load_status()
    data["roster"][args.role]["status"] = args.status
    data["roster"][args.role]["active_task"] = args.task
    save_status(data)
    print(f"{args.role} -> {args.status} (task: {args.task or 'None'})")
    return 0


def cmd_enqueue(args: argparse.Namespace) -> int:
    data = load_status()
    if any(item.get("pr_id") == args.pr_id for item in data["review_queue"]):
        print(f"ERROR: {args.pr_id} is already queued.", file=sys.stderr)
        return 1
    data["review_queue"].append(
        {"pr_id": args.pr_id, "title": args.title, "assignee": args.assignee}
    )
    save_status(data)
    print(f"Queued {args.pr_id} for review (assignee: {args.assignee or 'Unassigned'}).")
    return 0


def cmd_dequeue(args: argparse.Namespace) -> int:
    data = load_status()
    remaining = [item for item in data["review_queue"] if item.get("pr_id") != args.pr_id]
    if len(remaining) == len(data["review_queue"]):
        print(f"ERROR: {args.pr_id} is not in the queue.", file=sys.stderr)
        return 1
    data["review_queue"] = remaining
    save_status(data)
    print(f"Removed {args.pr_id} from the review queue.")
    return 0


def cmd_reset(_: argparse.Namespace) -> int:
    save_status(default_status())
    print("Roster and review queue reset to defaults.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command")

    show = sub.add_parser("show", help="Print the current roster and review queue.")
    show.add_argument("--json", action="store_true")
    show.set_defaults(func=cmd_show)

    set_cmd = sub.add_parser("set", help="Update an agent's state.")
    set_cmd.add_argument("role", choices=ROLES)
    set_cmd.add_argument("status", choices=STATES)
    set_cmd.add_argument("--task", default=None)
    set_cmd.set_defaults(func=cmd_set)

    enqueue = sub.add_parser("enqueue", help="Add a pull request to the review queue.")
    enqueue.add_argument("pr_id")
    enqueue.add_argument("--title", default="Untitled")
    enqueue.add_argument("--assignee", default=None)
    enqueue.set_defaults(func=cmd_enqueue)

    dequeue = sub.add_parser("dequeue", help="Remove a pull request from the review queue.")
    dequeue.add_argument("pr_id")
    dequeue.set_defaults(func=cmd_dequeue)

    reset = sub.add_parser("reset", help="Reset roster and queue to defaults.")
    reset.set_defaults(func=cmd_reset)

    parser.set_defaults(func=cmd_show, json=False)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
