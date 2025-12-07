"""
Spec-to-Code Helper Script

Automates conversion from specifications to implementation artifacts.

Commands:
    generate-tests    Generate test stubs from acceptance criteria
    verify-coverage   Verify all ACs have corresponding tests
    generate-checklist Generate implementation checklist from spec
    extract-contracts Extract technical contracts from spec
    create-matrix     Create traceability matrix

Usage:
    python helper.py generate-tests --spec <spec-file> --output <test-file>
    python helper.py verify-coverage --spec <spec-file> --tests <tests-dir>
    python helper.py generate-checklist --spec <spec-file>
    python helper.py extract-contracts --spec <spec-file>
    python helper.py create-matrix --spec <spec-file> --tests <tests-dir> --code <code-dir>
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class AcceptanceCriterion:
    """Represents a single acceptance criterion from spec."""
    id: str  # AC1, AC2, etc.
    description: str
    category: str  # happy_path, validation, system_behavior, etc.


@dataclass
class TestStub:
    """Represents a generated test stub."""
    function_name: str
    docstring: str
    ac_ref: str
    test_body: str


@dataclass
class Contract:
    """Represents a technical contract from spec."""
    type: str  # model, service, cli
    name: str
    signature: str
    description: str


class SpecParser:
    """Parse specification documents to extract ACs and contracts."""

    @staticmethod
    def extract_acceptance_criteria(spec_path: Path) -> List[AcceptanceCriterion]:
        """
        Extract all acceptance criteria from spec.

        Args:
            spec_path: Path to spec markdown file

        Returns:
            List of AcceptanceCriterion objects

        Raises:
            FileNotFoundError: If spec file not found
        """
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec not found: {spec_path}")

        content = spec_path.read_text(encoding="utf-8")

        # Pattern: - **AC1**: Description text
        pattern = r'\*\*AC(\d+)\*\*:\s*(.+?)(?:\n|$)'
        matches = re.findall(pattern, content, re.MULTILINE)

        criteria = []
        for num, desc in matches:
            ac_id = f"AC{num}"
            category = SpecParser._categorize_ac(desc)
            criteria.append(
                AcceptanceCriterion(
                    id=ac_id,
                    description=desc.strip(),
                    category=category
                )
            )

        return criteria

    @staticmethod
    def _categorize_ac(description: str) -> str:
        """Categorize AC by type based on description keywords."""
        desc_lower = description.lower()

        if "validation error" in desc_lower or "must be" in desc_lower:
            return "validation"
        elif "optional" in desc_lower:
            return "optional_feature"
        elif "system" in desc_lower or "auto" in desc_lower:
            return "system_behavior"
        elif "display" in desc_lower or "shows" in desc_lower:
            return "ui_behavior"
        else:
            return "happy_path"

    @staticmethod
    def extract_contracts(spec_path: Path) -> List[Contract]:
        """Extract technical contracts (model, service, CLI) from spec."""
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec not found: {spec_path}")

        content = spec_path.read_text(encoding="utf-8")
        contracts = []

        # Extract Python code blocks
        code_pattern = r'```python\n(.*?)\n```'
        code_blocks = re.findall(code_pattern, content, re.DOTALL)

        for block in code_blocks:
            # Model contracts (dataclass)
            if "@dataclass" in block and "class " in block:
                match = re.search(r'class\s+(\w+):', block)
                if match:
                    contracts.append(Contract(
                        type="model",
                        name=match.group(1),
                        signature=block.strip(),
                        description=f"{match.group(1)} model contract"
                    ))

            # Service contracts (def methods)
            elif "def " in block and "self" in block:
                match = re.search(r'def\s+(\w+)\s*\(', block)
                if match:
                    contracts.append(Contract(
                        type="service",
                        name=match.group(1),
                        signature=block.strip(),
                        description=f"{match.group(1)} service method"
                    ))

        # Extract CLI contracts
        cli_pattern = r'```bash\n(todo\s+\w+.*?)\n```'
        cli_matches = re.findall(cli_pattern, content, re.DOTALL)

        for cli_cmd in cli_matches:
            cmd_name = cli_cmd.split()[1] if len(cli_cmd.split()) > 1 else "unknown"
            contracts.append(Contract(
                type="cli",
                name=cmd_name,
                signature=cli_cmd.strip(),
                description=f"CLI command: {cmd_name}"
            ))

        return contracts


class TestGenerator:
    """Generate test stubs from acceptance criteria."""

    @staticmethod
    def generate_test_stubs(
        criteria: List[AcceptanceCriterion],
        test_class_name: str = "TestFeature"
    ) -> List[TestStub]:
        """
        Generate test function stubs from acceptance criteria.

        Args:
            criteria: List of acceptance criteria
            test_class_name: Name of test class

        Returns:
            List of TestStub objects
        """
        stubs = []

        for ac in criteria:
            stub = TestGenerator._create_stub_for_ac(ac)
            stubs.append(stub)

        return stubs

    @staticmethod
    def _create_stub_for_ac(ac: AcceptanceCriterion) -> TestStub:
        """Create test stub for a single AC."""
        # Generate function name from description
        func_name = TestGenerator._description_to_function_name(ac.description)

        # Create docstring
        docstring = f'"""{ac.description} ({ac.id})."""'

        # Create test body based on category
        if ac.category == "validation":
            test_body = f'''with pytest.raises(ValidationError):
            # TODO: Implement test for {ac.id}
            pass'''
        elif ac.category == "happy_path":
            test_body = f'''# Arrange
        # TODO: Set up test data for {ac.id}

        # Act
        # TODO: Execute the code being tested

        # Assert
        # TODO: Verify expected behavior for {ac.id}
        pytest.fail("IMPLEMENT ME: {ac.id}")'''
        else:
            test_body = f'''# TODO: Implement test for {ac.id}
        pytest.fail("IMPLEMENT ME: {ac.id}")'''

        return TestStub(
            function_name=func_name,
            docstring=docstring,
            ac_ref=ac.id,
            test_body=test_body
        )

    @staticmethod
    def _description_to_function_name(description: str) -> str:
        """Convert AC description to snake_case function name."""
        # Remove special characters and convert to lowercase
        desc = re.sub(r'[^\w\s]', '', description.lower())

        # Take first 6-8 meaningful words
        words = desc.split()[:8]

        # Join with underscores
        func_name = "_".join(words)

        # Prepend "test_"
        return f"test_{func_name}"

    @staticmethod
    def write_test_file(
        stubs: List[TestStub],
        output_path: Path,
        spec_ref: str
    ) -> None:
        """
        Write test stubs to file.

        Args:
            stubs: List of test stubs
            output_path: Path to output test file
            spec_ref: Spec reference (e.g., "001-add-task")
        """
        header = f'''"""
Unit tests for feature (Spec: {spec_ref}).

Tests cover:
{TestGenerator._generate_test_summary(stubs)}
"""
import pytest
from src.models.exceptions import ValidationError


class TestFeature:
    """Test feature implementation."""

'''

        test_functions = []
        for stub in stubs:
            func = f'''    def {stub.function_name}(self):  # {stub.ac_ref}
        {stub.docstring}
        {TestGenerator._indent_body(stub.test_body)}

'''
            test_functions.append(func)

        content = header + "\n".join(test_functions)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")

        print(f"✅ Generated {len(stubs)} test stubs → {output_path}")

    @staticmethod
    def _generate_test_summary(stubs: List[TestStub]) -> str:
        """Generate summary comment of what tests cover."""
        ac_refs = [stub.ac_ref for stub in stubs]
        return f"- {', '.join(ac_refs)}"

    @staticmethod
    def _indent_body(body: str) -> str:
        """Indent test body correctly."""
        lines = body.split("\n")
        return "\n        ".join(lines)


class CoverageVerifier:
    """Verify test coverage of acceptance criteria."""

    @staticmethod
    def verify_coverage(
        criteria: List[AcceptanceCriterion],
        tests_dir: Path
    ) -> Tuple[List[str], List[str]]:
        """
        Verify all ACs have corresponding tests.

        Args:
            criteria: List of acceptance criteria
            tests_dir: Directory containing test files

        Returns:
            Tuple of (covered_acs, missing_acs)
        """
        if not tests_dir.exists():
            return [], [ac.id for ac in criteria]

        # Read all test files
        test_files = list(tests_dir.glob("**/*.py"))
        all_test_content = ""

        for test_file in test_files:
            all_test_content += test_file.read_text(encoding="utf-8")

        # Check each AC
        covered = []
        missing = []

        for ac in criteria:
            # Look for AC reference in test comments or docstrings
            pattern = rf'#\s*{ac.id}|{ac.id}[:\)]'

            if re.search(pattern, all_test_content):
                covered.append(ac.id)
            else:
                missing.append(ac.id)

        return covered, missing

    @staticmethod
    def print_coverage_report(
        criteria: List[AcceptanceCriterion],
        covered: List[str],
        missing: List[str]
    ) -> None:
        """Print coverage report."""
        total = len(criteria)
        covered_count = len(covered)
        coverage_pct = (covered_count / total * 100) if total > 0 else 0

        print(f"\n📊 Acceptance Criteria Coverage Report")
        print(f"{'=' * 50}")
        print(f"Total ACs: {total}")
        print(f"Covered: {covered_count} ({coverage_pct:.1f}%)")
        print(f"Missing: {len(missing)}")

        if missing:
            print(f"\n❌ Missing test coverage for:")
            for ac_id in missing:
                ac = next((c for c in criteria if c.id == ac_id), None)
                if ac:
                    print(f"   - {ac_id}: {ac.description}")

        if covered_count == total:
            print(f"\n✅ All acceptance criteria have test coverage!")
        else:
            print(f"\n⚠️  {len(missing)} acceptance criteria need tests")


class ChecklistGenerator:
    """Generate implementation checklists from specs."""

    @staticmethod
    def generate_checklist(
        criteria: List[AcceptanceCriterion],
        contracts: List[Contract]
    ) -> str:
        """
        Generate implementation checklist.

        Args:
            criteria: List of acceptance criteria
            contracts: List of technical contracts

        Returns:
            Markdown checklist
        """
        checklist = f"""# Implementation Checklist

## Acceptance Criteria

"""

        for ac in criteria:
            checklist += f"- [ ] **{ac.id}**: {ac.description}\n"

        checklist += "\n## Technical Contracts\n\n"

        for contract in contracts:
            checklist += f"- [ ] {contract.type.upper()}: {contract.name}\n"

        checklist += """
## Quality Gates

- [ ] All tests pass: `pytest`
- [ ] Type check passes: `mypy --strict src/`
- [ ] Linter passes: `ruff check src/ tests/`
- [ ] Formatter passes: `ruff format --check src/ tests/`
- [ ] Coverage >90%: `pytest --cov=src --cov-fail-under=90`

## Traceability

- [ ] All tests reference ACs in docstrings
- [ ] All code references spec in docstrings
- [ ] Traceability matrix created

## Verification

- [ ] All ACs have passing tests
- [ ] Contracts match spec exactly
- [ ] Error messages user-friendly
- [ ] Documentation updated
"""

        return checklist


class MatrixGenerator:
    """Generate traceability matrices."""

    @staticmethod
    def create_traceability_matrix(
        criteria: List[AcceptanceCriterion],
        tests_dir: Path,
        code_dir: Path
    ) -> str:
        """
        Create traceability matrix linking ACs to tests and code.

        Args:
            criteria: List of acceptance criteria
            tests_dir: Directory containing tests
            code_dir: Directory containing source code

        Returns:
            Markdown table of traceability matrix
        """
        matrix = f"""# Traceability Matrix

| AC | Description | Tests | Code |
|----|-------------|-------|------|
"""

        for ac in criteria:
            tests = MatrixGenerator._find_tests_for_ac(ac.id, tests_dir)
            code_locs = MatrixGenerator._find_code_for_ac(ac.id, code_dir)

            tests_str = ", ".join(tests) if tests else "⚠️ No tests"
            code_str = ", ".join(code_locs) if code_locs else "⚠️ No implementation"

            matrix += f"| {ac.id} | {ac.description[:50]}... | {tests_str} | {code_str} |\n"

        return matrix

    @staticmethod
    def _find_tests_for_ac(ac_id: str, tests_dir: Path) -> List[str]:
        """Find all test functions that reference an AC."""
        if not tests_dir.exists():
            return []

        tests = []
        test_files = list(tests_dir.glob("**/*.py"))

        for test_file in test_files:
            content = test_file.read_text(encoding="utf-8")

            # Find test functions with AC reference
            pattern = rf'def\s+(test_\w+)\s*\(.*?\).*?#\s*{ac_id}'
            matches = re.findall(pattern, content, re.MULTILINE)

            for match in matches:
                tests.append(f"`{match}()`")

        return tests

    @staticmethod
    def _find_code_for_ac(ac_id: str, code_dir: Path) -> List[str]:
        """Find code locations that reference an AC."""
        if not code_dir.exists():
            return []

        locations = []
        code_files = list(code_dir.glob("**/*.py"))

        for code_file in code_files:
            content = code_file.read_text(encoding="utf-8")

            # Look for AC references in comments/docstrings
            if ac_id in content:
                relative_path = code_file.relative_to(code_dir.parent)
                locations.append(str(relative_path))

        return locations


# CLI Interface

def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "generate-tests":
        generate_tests_command()
    elif command == "verify-coverage":
        verify_coverage_command()
    elif command == "generate-checklist":
        generate_checklist_command()
    elif command == "extract-contracts":
        extract_contracts_command()
    elif command == "create-matrix":
        create_matrix_command()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


def generate_tests_command():
    """Generate test stubs from spec."""
    if "--spec" not in sys.argv or "--output" not in sys.argv:
        print("Usage: generate-tests --spec <spec-file> --output <test-file>")
        sys.exit(1)

    spec_path = Path(sys.argv[sys.argv.index("--spec") + 1])
    output_path = Path(sys.argv[sys.argv.index("--output") + 1])

    print(f"📖 Reading spec: {spec_path}")
    criteria = SpecParser.extract_acceptance_criteria(spec_path)

    print(f"✓ Found {len(criteria)} acceptance criteria")

    stubs = TestGenerator.generate_test_stubs(criteria)

    spec_ref = spec_path.stem
    TestGenerator.write_test_file(stubs, output_path, spec_ref)


def verify_coverage_command():
    """Verify test coverage of ACs."""
    if "--spec" not in sys.argv or "--tests" not in sys.argv:
        print("Usage: verify-coverage --spec <spec-file> --tests <tests-dir>")
        sys.exit(1)

    spec_path = Path(sys.argv[sys.argv.index("--spec") + 1])
    tests_dir = Path(sys.argv[sys.argv.index("--tests") + 1])

    print(f"📖 Reading spec: {spec_path}")
    criteria = SpecParser.extract_acceptance_criteria(spec_path)

    print(f"🔍 Checking test coverage in: {tests_dir}")
    covered, missing = CoverageVerifier.verify_coverage(criteria, tests_dir)

    CoverageVerifier.print_coverage_report(criteria, covered, missing)

    # Exit with error if coverage incomplete
    if missing:
        sys.exit(1)


def generate_checklist_command():
    """Generate implementation checklist."""
    if "--spec" not in sys.argv:
        print("Usage: generate-checklist --spec <spec-file>")
        sys.exit(1)

    spec_path = Path(sys.argv[sys.argv.index("--spec") + 1])

    print(f"📖 Reading spec: {spec_path}")
    criteria = SpecParser.extract_acceptance_criteria(spec_path)
    contracts = SpecParser.extract_contracts(spec_path)

    checklist = ChecklistGenerator.generate_checklist(criteria, contracts)

    print("\n" + checklist)


def extract_contracts_command():
    """Extract technical contracts from spec."""
    if "--spec" not in sys.argv:
        print("Usage: extract-contracts --spec <spec-file>")
        sys.exit(1)

    spec_path = Path(sys.argv[sys.argv.index("--spec") + 1])

    print(f"📖 Reading spec: {spec_path}")
    contracts = SpecParser.extract_contracts(spec_path)

    print(f"\n✓ Found {len(contracts)} contracts:")
    for contract in contracts:
        print(f"\n{contract.type.upper()}: {contract.name}")
        print(f"```python\n{contract.signature}\n```")


def create_matrix_command():
    """Create traceability matrix."""
    if "--spec" not in sys.argv or "--tests" not in sys.argv or "--code" not in sys.argv:
        print("Usage: create-matrix --spec <spec-file> --tests <tests-dir> --code <code-dir>")
        sys.exit(1)

    spec_path = Path(sys.argv[sys.argv.index("--spec") + 1])
    tests_dir = Path(sys.argv[sys.argv.index("--tests") + 1])
    code_dir = Path(sys.argv[sys.argv.index("--code") + 1])

    print(f"📖 Reading spec: {spec_path}")
    criteria = SpecParser.extract_acceptance_criteria(spec_path)

    print(f"🔍 Creating traceability matrix...")
    matrix = MatrixGenerator.create_traceability_matrix(criteria, tests_dir, code_dir)

    print("\n" + matrix)


if __name__ == "__main__":
    main()
