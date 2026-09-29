#!/usr/bin/env python3
"""Lock test files after the red phase and block agent edits until unlocked."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

STATE_FILE = Path(".agent/test-lock.json")


def normalize(path: str) -> str:
    candidate = Path(path)
    try:
        return candidate.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return candidate.resolve().as_posix()


def load_locked() -> list[str]:
    if not STATE_FILE.exists():
        return []
    try:
        data = json.loads(STATE_FILE.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"{STATE_FILE} is corrupt: {exc}") from exc
    paths = data.get("locked_paths", [])
    if not isinstance(paths, list) or not all(isinstance(path, str) for path in paths):
        raise ValueError(f"{STATE_FILE}: locked_paths must be a list of strings")
    return paths


def save_locked(paths: list[str]) -> None:
    if not paths:
        STATE_FILE.unlink(missing_ok=True)
        return
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({"locked_paths": sorted(set(paths))}, indent=2) + "\n")


def cmd_lock(args: argparse.Namespace) -> int:
    missing = [path for path in args.paths if not Path(path).exists()]
    if missing:
        print(f"ERROR: cannot lock missing path(s): {', '.join(missing)}", file=sys.stderr)
        return 1
    locked = set(load_locked())
    locked.update(normalize(path) for path in args.paths)
    save_locked(list(locked))
    print(f"Test guard locked {len(locked)} path(s).")
    return 0


def cmd_unlock(args: argparse.Namespace) -> int:
    if args.all:
        save_locked([])
        print("Test guard unlocked all paths.")
        return 0
    locked = set(load_locked())
    locked.difference_update(normalize(path) for path in args.paths)
    save_locked(list(locked))
    print(f"Test guard has {len(locked)} locked path(s).")
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    locked = load_locked()
    if not locked:
        print("Test guard: unlocked")
        return 0
    print("Test guard: locked")
    for path in locked:
        print(f"  {path}")
    return 0


def find_paths(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"file_path", "path"} and isinstance(child, str):
                found.append(child)
            else:
                found.extend(find_paths(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(find_paths(child))
    return found


def is_within(target: str, locked: str) -> bool:
    target_path = Path(target)
    locked_path = Path(locked)
    return target_path == locked_path or locked_path in target_path.parents


def cmd_check_hook(_: argparse.Namespace) -> int:
    locked = load_locked()
    if not locked:
        return 0
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("BLOCKED: test guard could not parse the edit event.", file=sys.stderr)
        return 2
    targets = [normalize(path) for path in find_paths(event)]
    blocked = [target for target in targets if any(is_within(target, path) for path in locked)]
    if blocked:
        print(
            "BLOCKED: test files are locked after the red phase: " + ", ".join(blocked),
            file=sys.stderr,
        )
        print("Run `python3 scripts/test_guard.py unlock --all` after implementation is green.", file=sys.stderr)
        return 2
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    lock = sub.add_parser("lock", help="Lock one or more test files/directories.")
    lock.add_argument("paths", nargs="+")
    lock.set_defaults(func=cmd_lock)

    unlock = sub.add_parser("unlock", help="Unlock paths after the implementation is green.")
    unlock.add_argument("paths", nargs="*")
    unlock.add_argument("--all", action="store_true")
    unlock.set_defaults(func=cmd_unlock)

    status = sub.add_parser("status", help="Show locked test paths.")
    status.set_defaults(func=cmd_status)

    hook = sub.add_parser("check-hook", help=argparse.SUPPRESS)
    hook.set_defaults(func=cmd_check_hook)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "unlock" and not args.all and not args.paths:
        print("ERROR: provide paths or --all.", file=sys.stderr)
        return 1
    try:
        return int(args.func(args))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
