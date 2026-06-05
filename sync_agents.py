#!/usr/bin/env python
# /// script
# requires-python = ">=3.10"
# ///
"""
sync_agents.py — Sync .agents/ from current branch into main.

Captures the current state of .agents/ (committed + uncommitted changes),
switches to main, applies the diff, commits, and returns to the original branch.
Only .agents/ is touched — nothing else.

Usage:
    uv run python sync_agents.py            # sync .agents/ to main
    uv run python sync_agents.py --dry-run  # preview what would change, no commit
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AGENTS_DIR = ROOT / ".agents"


class SyncError(Exception):
    pass


def run(cmd: list[str], *, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=ROOT,
        check=check,
        capture_output=capture,
        text=True,
    )


def capture(cmd: list[str]) -> str:
    result = run(cmd, capture=True)
    return result.stdout.strip()


def current_branch() -> str:
    branch = capture(["git", "branch", "--show-current"])
    if not branch:
        raise SyncError("Detached HEAD — checkout a named branch first.")
    return branch


def has_uncommitted_changes(path: str = ".agents") -> bool:
    result = run(["git", "status", "--porcelain", path], capture=True, check=False)
    return bool(result.stdout.strip())


def branch_exists(name: str) -> bool:
    result = run(["git", "rev-parse", "--verify", name], capture=True, check=False)
    return result.returncode == 0


def agents_diff_summary(from_ref: str, to_ref: str) -> list[str]:
    """List files changed in .agents/ between two refs."""
    result = run(
        ["git", "diff", "--name-only", from_ref, to_ref, "--", ".agents/"],
        capture=True,
        check=False,
    )
    return [line for line in result.stdout.splitlines() if line]


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync .agents/ from current branch to main.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without committing.")
    args = parser.parse_args()

    try:
        source_branch = current_branch()

        if source_branch == "main":
            print("Already on main. Nothing to sync.")
            return 0

        if not branch_exists("main"):
            raise SyncError("'main' branch not found in this repo.")

        if not AGENTS_DIR.exists():
            raise SyncError(".agents/ directory not found.")

        # --- Save current working-tree state of .agents/ ---
        tmp = tempfile.mkdtemp(prefix="sync_agents_")
        tmp_agents = Path(tmp) / ".agents"
        shutil.copytree(AGENTS_DIR, tmp_agents)
        print(f"Saved .agents/ ({_count_files(tmp_agents)} files) from branch '{source_branch}'.")

        uncommitted = has_uncommitted_changes()
        stashed = False

        try:
            # --- Stash if working tree is dirty (to allow branch switch) ---
            if uncommitted:
                if args.dry_run:
                    print("(dry-run) Would stash uncommitted changes to switch branches.")
                else:
                    result = run(
                        ["git", "stash", "push", "--include-untracked", "-m", "sync_agents: temp stash"],
                        capture=True,
                    )
                    stashed = "No local changes" not in result.stdout
                    if stashed:
                        print("Stashed uncommitted changes (will restore after sync).")

            # --- Switch to main ---
            if args.dry_run:
                print("(dry-run) Would switch to main.")
                _preview_diff(tmp_agents, source_branch)
                return 0
            else:
                run(["git", "checkout", "main"])
                print("Switched to main.")

            # --- Replace .agents/ with saved state ---
            if AGENTS_DIR.exists():
                shutil.rmtree(AGENTS_DIR)
            shutil.copytree(tmp_agents, AGENTS_DIR)

            # --- Commit if there are changes ---
            run(["git", "add", ".agents/"])
            diff_result = run(["git", "diff", "--cached", "--stat", "--", ".agents/"], capture=True, check=False)
            staged_stat = diff_result.stdout.strip()

            if not staged_stat:
                print("No changes in .agents/ compared to main. Nothing to commit.")
            else:
                print("\nChanges to commit:\n" + staged_stat)
                commit_msg = f"sync .agents/ from {source_branch}"
                run(["git", "commit", "-m", commit_msg])
                print(f"\nCommitted to main: \"{commit_msg}\"")

        finally:
            # --- Always return to original branch ---
            if not args.dry_run:
                run(["git", "checkout", source_branch])
                print(f"Returned to '{source_branch}'.")

                if stashed:
                    run(["git", "stash", "pop"])
                    print("Restored stashed changes.")

            shutil.rmtree(tmp, ignore_errors=True)

    except SyncError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as exc:
        print(f"Git error: {exc.stderr or exc}", file=sys.stderr)
        return 1

    return 0


def _count_files(path: Path) -> int:
    return sum(1 for _ in path.rglob("*") if _.is_file())


def _preview_diff(tmp_agents: Path, source_branch: str) -> None:
    """Show what would change in .agents/ between main and current saved state."""
    result = subprocess.run(
        ["git", "diff", "main", "--", ".agents/"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    # Also count uncommitted changes captured in tmp_agents
    committed_diff = agents_diff_summary("main", "HEAD")
    uncommitted = has_uncommitted_changes()

    print(f"\n--- Preview: .agents/ changes from '{source_branch}' to main ---")
    if committed_diff:
        print(f"Committed changes ({len(committed_diff)} files):")
        for f in committed_diff:
            print(f"  {f}")
    if uncommitted:
        print("Uncommitted changes also captured (see git status .agents/).")
    if not committed_diff and not uncommitted:
        print("No changes in .agents/ — nothing would be committed.")
    print("---")


if __name__ == "__main__":
    raise SystemExit(main())
