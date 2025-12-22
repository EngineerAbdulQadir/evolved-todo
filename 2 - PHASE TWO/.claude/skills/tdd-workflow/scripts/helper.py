#!/usr/bin/env python3
"""
TDD Workflow Helper Script

Automates TDD cycle steps and tracks cycle timing.
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Tuple, List


class TDDCycleTimer:
    """Track timing for TDD cycles."""

    def __init__(self) -> None:
        self.red_start: float = 0
        self.green_start: float = 0
        self.refactor_start: float = 0

    def start_red(self) -> None:
        """Start red phase timer."""
        self.red_start = time.time()
        print("=4 RED PHASE: Writing failing test...")

    def end_red_start_green(self) -> None:
        """End red phase, start green phase."""
        red_duration = time.time() - self.red_start
        print(f" Red phase: {red_duration:.1f}s")
        self.green_start = time.time()
        print("=â GREEN PHASE: Making test pass...")

    def end_green_start_refactor(self) -> None:
        """End green phase, start refactor phase."""
        green_duration = time.time() - self.green_start
        print(f" Green phase: {green_duration:.1f}s")
        self.refactor_start = time.time()
        print("=5 REFACTOR PHASE: Improving code...")

    def end_refactor(self) -> None:
        """End refactor phase."""
        refactor_duration = time.time() - self.refactor_start
        total = time.time() - self.red_start
        print(f" Refactor phase: {refactor_duration:.1f}s")
        print(f" Total cycle: {total:.1f}s")


def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """Run shell command and return exit code, stdout, stderr."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def run_tests(test_path: str = "tests/") -> bool:
    """Run pytest on specified path."""
    print(f"\n>ê Running tests: {test_path}")
    code, stdout, stderr = run_command(["uv", "run", "pytest", test_path, "-v"])

    print(stdout)
    if stderr:
        print(stderr)

    return code == 0


def run_specific_test(test_file: str, test_name: str = "") -> bool:
    """Run a specific test."""
    test_path = f"{test_file}::{test_name}" if test_name else test_file
    print(f"\n>ê Running test: {test_path}")

    code, stdout, stderr = run_command([
        "uv", "run", "pytest", test_path, "-v"
    ])

    print(stdout)
    if stderr:
        print(stderr)

    return code == 0


def run_quality_checks() -> bool:
    """Run all quality checks (mypy, ruff, pytest)."""
    checks = [
        (["uv", "run", "mypy", "--strict", "src/"], "Type checking"),
        (["uv", "run", "ruff", "check", "src/", "tests/"], "Linting"),
        (["uv", "run", "pytest"], "Tests"),
    ]

    print("\n= Running quality checks...")

    for cmd, name in checks:
        print(f"\n’ {name}...")
        code, stdout, stderr = run_command(cmd)

        if code != 0:
            print(f"L {name} failed!")
            print(stdout)
            print(stderr)
            return False

        print(f" {name} passed")

    return True


def git_commit_tdd_phase(phase: str, message: str) -> bool:
    """Commit changes for TDD phase."""
    phases = {
        "red": "test",
        "green": "feat",
        "refactor": "refactor"
    }

    if phase not in phases:
        print(f"L Invalid phase: {phase}")
        return False

    commit_type = phases[phase]

    # Stage all changes
    code, _, _ = run_command(["git", "add", "."])
    if code != 0:
        print("L git add failed")
        return False

    # Commit with message
    full_message = f"{commit_type}: {message}\n\n[TDD {phase.upper()} phase]"
    code, _, _ = run_command(["git", "commit", "-m", full_message])

    if code != 0:
        print("L git commit failed")
        return False

    print(f" Committed: {commit_type}: {message}")
    return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("TDD Workflow Helper\n")
        print("Usage:")
        print("  helper.py red <test-file>         # Run test (expect failure)")
        print("  helper.py green <test-file>       # Run test (expect pass)")
        print("  helper.py refactor                # Run quality checks")
        print("  helper.py commit <phase> <msg>    # Commit TDD phase")
        print("  helper.py cycle <test-file>       # Full TDD cycle with timing")
        sys.exit(1)

    command = sys.argv[1]

    if command == "red":
        if len(sys.argv) < 3:
            print("L Test file required")
            sys.exit(1)

        test_file = sys.argv[2]
        print("=4 RED PHASE")
        success = run_specific_test(test_file)

        if success:
            print("   Warning: Test passed! Expected failure in RED phase.")
        else:
            print(" Test failed as expected. Now make it pass (GREEN phase).")

    elif command == "green":
        if len(sys.argv) < 3:
            print("L Test file required")
            sys.exit(1)

        test_file = sys.argv[2]
        print("=â GREEN PHASE")
        success = run_specific_test(test_file)

        if not success:
            print("L Test still failing. Keep working on implementation.")
            sys.exit(1)
        else:
            print(" Test passed! Now refactor (REFACTOR phase).")

    elif command == "refactor":
        print("=5 REFACTOR PHASE")
        if not run_quality_checks():
            print("L Quality checks failed. Fix issues before committing.")
            sys.exit(1)
        print(" All quality checks passed!")

    elif command == "commit":
        if len(sys.argv) < 4:
            print("L Phase and message required")
            print("Example: helper.py commit red 'add failing test for validation'")
            sys.exit(1)

        phase = sys.argv[2]
        message = sys.argv[3]

        if not git_commit_tdd_phase(phase, message):
            sys.exit(1)

    elif command == "cycle":
        if len(sys.argv) < 3:
            print("L Test file required")
            sys.exit(1)

        test_file = sys.argv[2]
        timer = TDDCycleTimer()

        # RED
        timer.start_red()
        input("Write your failing test, then press Enter...")
        run_specific_test(test_file)

        # GREEN
        timer.end_red_start_green()
        input("Implement code to make test pass, then press Enter...")
        success = run_specific_test(test_file)
        if not success:
            print("L Test still failing. Keep working.")
            sys.exit(1)

        # REFACTOR
        timer.end_green_start_refactor()
        input("Refactor if needed, then press Enter...")
        if not run_quality_checks():
            print("L Quality checks failed")
            sys.exit(1)

        timer.end_refactor()
        print("\n<‰ TDD cycle complete!")

    else:
        print(f"L Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
