#!/usr/bin/env python3
"""
Quality Check Helper Script

Automates quality gate checks with detailed reporting.
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CheckResult:
    """Result of a quality check."""

    name: str
    passed: bool
    duration: float
    output: str
    error: Optional[str] = None


class QualityChecker:
    """Run quality checks and generate reports."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[CheckResult] = []

    def run_command(
        self,
        cmd: List[str],
        name: str,
        cwd: Optional[Path] = None
    ) -> CheckResult:
        """Run a command and capture results."""
        if self.verbose:
            print(f"\n{'=' * 60}")
            print(f"Running: {name}")
            print(f"Command: {' '.join(cmd)}")
            print(f"{'=' * 60}\n")

        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=300  # 5 minute timeout
            )

            duration = time.time() - start_time
            passed = result.returncode == 0

            output = result.stdout
            error = result.stderr if result.stderr else None

            if self.verbose or not passed:
                print(output)
                if error:
                    print(error)

            status = " PASSED" if passed else "L FAILED"
            print(f"{status}: {name} ({duration:.2f}s)")

            return CheckResult(
                name=name,
                passed=passed,
                duration=duration,
                output=output,
                error=error
            )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"L TIMEOUT: {name} ({duration:.2f}s)")

            return CheckResult(
                name=name,
                passed=False,
                duration=duration,
                output="",
                error="Command timed out after 5 minutes"
            )

        except Exception as e:
            duration = time.time() - start_time
            print(f"L ERROR: {name} ({duration:.2f}s)")
            print(f"Error: {e}")

            return CheckResult(
                name=name,
                passed=False,
                duration=duration,
                output="",
                error=str(e)
            )

    def check_mypy(self) -> CheckResult:
        """Run mypy type checking."""
        result = self.run_command(
            ["uv", "run", "mypy", "--strict", "src/"],
            "Type Checking (mypy)"
        )
        self.results.append(result)
        return result

    def check_ruff_lint(self) -> CheckResult:
        """Run ruff linting."""
        result = self.run_command(
            ["uv", "run", "ruff", "check", "src/", "tests/"],
            "Linting (ruff check)"
        )
        self.results.append(result)
        return result

    def check_ruff_format(self) -> CheckResult:
        """Run ruff format check."""
        result = self.run_command(
            ["uv", "run", "ruff", "format", "--check", "src/", "tests/"],
            "Formatting (ruff format)"
        )
        self.results.append(result)
        return result

    def check_tests(self, coverage_threshold: int = 90) -> CheckResult:
        """Run pytest with coverage."""
        result = self.run_command(
            [
                "uv", "run", "pytest",
                "--cov=src",
                f"--cov-fail-under={coverage_threshold}",
                "-v" if self.verbose else "-q"
            ],
            f"Testing (pytest, coverage >={coverage_threshold}%)"
        )
        self.results.append(result)
        return result

    def check_security(self) -> CheckResult:
        """Run pip-audit security check."""
        result = self.run_command(
            ["uv", "run", "pip-audit"],
            "Security Audit (pip-audit)"
        )
        self.results.append(result)
        return result

    def print_summary(self) -> bool:
        """Print summary of all checks and return overall status."""
        print("\n" + "=" * 60)
        print("QUALITY CHECK SUMMARY")
        print("=" * 60)

        total_duration = sum(r.duration for r in self.results)
        passed_count = sum(1 for r in self.results if r.passed)
        total_count = len(self.results)

        for result in self.results:
            status = "" if result.passed else "L"
            print(f"{status} {result.name} ({result.duration:.2f}s)")

        print("=" * 60)
        print(f"Passed: {passed_count}/{total_count}")
        print(f"Total Duration: {total_duration:.2f}s")
        print("=" * 60)

        all_passed = all(r.passed for r in self.results)

        if all_passed:
            print("\n<‰ ALL QUALITY CHECKS PASSED!")
        else:
            print("\nL SOME QUALITY CHECKS FAILED")

            # Print failure details
            print("\nFailure Details:")
            for result in self.results:
                if not result.passed:
                    print(f"\n{result.name}:")
                    if result.error:
                        print(f"  Error: {result.error}")
                    # Print last few lines of output
                    lines = result.output.strip().split("\n")[-5:]
                    for line in lines:
                        print(f"  {line}")

        return all_passed


def run_quick_check(verbose: bool = False) -> bool:
    """Run quick quality checks (type + lint only)."""
    print("<Ã Running Quick Quality Check (type + lint)\n")

    checker = QualityChecker(verbose=verbose)

    checker.check_mypy()
    checker.check_ruff_lint()

    return checker.print_summary()


def run_full_check(verbose: bool = False, coverage: int = 90) -> bool:
    """Run full quality checks (all gates)."""
    print("= Running Full Quality Check (all gates)\n")

    checker = QualityChecker(verbose=verbose)

    # Run all checks
    checker.check_mypy()
    checker.check_ruff_lint()
    checker.check_ruff_format()
    checker.check_tests(coverage_threshold=coverage)

    return checker.print_summary()


def run_pre_commit_check(verbose: bool = False) -> bool:
    """Run pre-commit quality checks."""
    print("= Running Pre-Commit Quality Check\n")

    checker = QualityChecker(verbose=verbose)

    # Essential checks only (fast)
    checker.check_mypy()
    checker.check_ruff_lint()
    checker.check_tests(coverage_threshold=90)

    return checker.print_summary()


def auto_fix() -> None:
    """Auto-fix linting and formatting issues."""
    print("=' Auto-Fixing Quality Issues\n")

    print("Fixing linting issues...")
    subprocess.run(["uv", "run", "ruff", "check", "--fix", "src/", "tests/"])

    print("\nFormatting code...")
    subprocess.run(["uv", "run", "ruff", "format", "src/", "tests/"])

    print("\n Auto-fix complete! Re-run quality check to verify.")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Quality Check Helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  helper.py quick              # Quick check (type + lint)
  helper.py full               # Full check (all gates)
  helper.py pre-commit         # Pre-commit check (fast)
  helper.py fix                # Auto-fix issues
  helper.py full --verbose     # Full check with verbose output
  helper.py full --coverage 95 # Require 95% coverage
        """
    )

    parser.add_argument(
        "command",
        choices=["quick", "full", "pre-commit", "fix"],
        help="Command to run"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "--coverage", "-c",
        type=int,
        default=90,
        help="Coverage threshold (default: 90)"
    )

    args = parser.parse_args()

    # Run selected command
    if args.command == "quick":
        success = run_quick_check(verbose=args.verbose)
    elif args.command == "full":
        success = run_full_check(verbose=args.verbose, coverage=args.coverage)
    elif args.command == "pre-commit":
        success = run_pre_commit_check(verbose=args.verbose)
    elif args.command == "fix":
        auto_fix()
        sys.exit(0)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
