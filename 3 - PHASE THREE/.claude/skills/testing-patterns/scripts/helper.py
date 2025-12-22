#!/usr/bin/env python3
"""
Test Code Generator

Generate boilerplate test files for models, services, and CLI commands.
"""

import sys
from pathlib import Path
from typing import List


# Test template for models
MODEL_TEST_TEMPLATE = '''"""
Unit tests for {model_class} model.
"""

import pytest
from src.models.{model_file} import {model_class}
from src.models.exceptions import ValidationError


class Test{model_class}Creation:
    """Test {model_class} initialization."""

    def test_create_valid_{model_var}(self) -> None:
        """Create {model_var} with valid data."""
        {model_var} = {model_class}(
            id=1,
            {required_field}="test value"
        )

        assert {model_var}.id == 1
        assert {model_var}.{required_field} == "test value"


class Test{model_class}Validation:
    """Test {model_class} validation rules."""

    def test_{field}_cannot_be_empty(self) -> None:
        """{Field} validation: cannot be empty."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            {model_class}(id=1, {field}="")

    def test_{field}_max_length(self) -> None:
        """{Field} validation: max length."""
        # TODO: Add max length validation test
        pass

    @pytest.mark.parametrize("{field},should_pass", [
        ("valid value", True),
        ("", False),
    ])
    def test_{field}_validation_parametrized(
        self,
        {field}: str,
        should_pass: bool
    ) -> None:
        """Test various {field} inputs."""
        if should_pass:
            {model_var} = {model_class}(id=1, {field}={field})
            assert {model_var}.{field} == {field}
        else:
            with pytest.raises(ValidationError):
                {model_class}(id=1, {field}={field})
'''

# Test template for services
SERVICE_TEST_TEMPLATE = '''"""
Unit tests for {service_class}.
"""

import pytest
from src.models.{model_file} import {model_class}
from src.models.exceptions import {model_class}NotFoundError, ValidationError
from src.services.{service_file} import {service_class}
from src.storage.in_memory_store import InMemory{model_class}Store
from src.lib.id_generator import SequentialIdGenerator


@pytest.fixture
def {model_var}_store() -> InMemory{model_class}Store:
    """Create fresh in-memory store."""
    return InMemory{model_class}Store()


@pytest.fixture
def id_gen() -> SequentialIdGenerator:
    """Create ID generator."""
    return SequentialIdGenerator(start=1)


@pytest.fixture
def {service_var}(
    {model_var}_store: InMemory{model_class}Store,
    id_gen: SequentialIdGenerator
) -> {service_class}:
    """Create configured service."""
    return {service_class}(store={model_var}_store, id_gen=id_gen)


class Test{service_class}Add:
    """Test add() method."""

    def test_add_{model_var}_success(self, {service_var}: {service_class}) -> None:
        """Add {model_var} with valid data succeeds."""
        {model_var} = {service_var}.add({required_field}="Test")

        assert isinstance({model_var}, {model_class})
        assert {model_var}.id == 1
        assert {model_var}.{required_field} == "Test"

    def test_add_multiple_{model_var}s_increments_id(
        self,
        {service_var}: {service_class}
    ) -> None:
        """Adding multiple {model_var}s increments ID."""
        {model_var}1 = {service_var}.add({required_field}="First")
        {model_var}2 = {service_var}.add({required_field}="Second")

        assert {model_var}1.id == 1
        assert {model_var}2.id == 2

    def test_add_{model_var}_validation_error(
        self,
        {service_var}: {service_class}
    ) -> None:
        """Add with invalid data raises ValidationError."""
        with pytest.raises(ValidationError):
            {service_var}.add({required_field}="")


class Test{service_class}Get:
    """Test get() method."""

    def test_get_existing_{model_var}(self, {service_var}: {service_class}) -> None:
        """Get existing {model_var} by ID."""
        created = {service_var}.add({required_field}="Test")
        retrieved = {service_var}.get(created.id)

        assert retrieved.id == created.id
        assert retrieved.{required_field} == created.{required_field}

    def test_get_nonexistent_{model_var}_raises(
        self,
        {service_var}: {service_class}
    ) -> None:
        """Get non-existent {model_var} raises error."""
        with pytest.raises({model_class}NotFoundError, match="not found"):
            {service_var}.get(999)


class Test{service_class}All:
    """Test all() method."""

    def test_all_returns_empty_initially(self, {service_var}: {service_class}) -> None:
        """All() returns empty list when no {model_var}s exist."""
        {model_var}s = {service_var}.all()

        assert {model_var}s == []

    def test_all_returns_sorted_{model_var}s(
        self,
        {service_var}: {service_class}
    ) -> None:
        """All() returns {model_var}s sorted by ID."""
        {service_var}.add({required_field}="First")
        {service_var}.add({required_field}="Second")

        {model_var}s = {service_var}.all()

        assert len({model_var}s) == 2
        assert [{model_var}.id for {model_var} in {model_var}s] == [1, 2]


class Test{service_class}Update:
    """Test update() method."""

    def test_update_{model_var}_{field}(self, {service_var}: {service_class}) -> None:
        """Update changes {field}."""
        {model_var} = {service_var}.add({required_field}="Original")

        updated = {service_var}.update({model_var}.id, {required_field}="Updated")

        assert updated.{required_field} == "Updated"
        assert updated.id == {model_var}.id


class Test{service_class}Delete:
    """Test delete() method."""

    def test_delete_existing_{model_var}(self, {service_var}: {service_class}) -> None:
        """Delete removes {model_var}."""
        {model_var} = {service_var}.add({required_field}="To delete")

        {service_var}.delete({model_var}.id)

        with pytest.raises({model_class}NotFoundError):
            {service_var}.get({model_var}.id)
'''

# Test template for CLI commands
CLI_TEST_TEMPLATE = '''"""
Integration tests for CLI commands.
"""

import pytest
from typer.testing import CliRunner
from src.main import app

runner = CliRunner()


class Test{command_name}Command:
    """Test '{command}' command."""

    def test_{command}_success(self) -> None:
        """{Command} with valid input succeeds."""
        result = runner.invoke(app, ["{command}", "test argument"])

        assert result.exit_code == 0
        assert "success" in result.stdout.lower()

    def test_{command}_with_options(self) -> None:
        """{Command} with options succeeds."""
        result = runner.invoke(app, [
            "{command}",
            "argument",
            "--option", "value"
        ])

        assert result.exit_code == 0

    def test_{command}_invalid_input_fails(self) -> None:
        """{Command} with invalid input returns error."""
        result = runner.invoke(app, ["{command}", ""])

        assert result.exit_code == 1
        assert "error" in result.stdout.lower()

    def test_{command}_nonexistent_resource_fails(self) -> None:
        """{Command} with non-existent resource fails."""
        result = runner.invoke(app, ["{command}", "999"])

        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()
'''


def to_snake_case(name: str) -> str:
    """Convert PascalCase to snake_case."""
    result = []
    for i, char in enumerate(name):
        if char.isupper() and i > 0:
            result.append('_')
        result.append(char.lower())
    return ''.join(result)


def generate_model_test(model_class: str, required_field: str = "title") -> str:
    """Generate model test file."""
    model_var = to_snake_case(model_class)
    model_file = model_var
    field = required_field

    return MODEL_TEST_TEMPLATE.format(
        model_class=model_class,
        model_var=model_var,
        model_file=model_file,
        required_field=required_field,
        field=field,
        Field=field.capitalize()
    )


def generate_service_test(
    model_class: str,
    service_class: str,
    required_field: str = "title"
) -> str:
    """Generate service test file."""
    model_var = to_snake_case(model_class)
    model_file = model_var
    service_var = to_snake_case(service_class)
    service_file = service_var

    return SERVICE_TEST_TEMPLATE.format(
        model_class=model_class,
        model_var=model_var,
        model_file=model_file,
        service_class=service_class,
        service_var=service_var,
        service_file=service_file,
        required_field=required_field,
        field=required_field
    )


def generate_cli_test(command_name: str) -> str:
    """Generate CLI test file."""
    command = command_name.lower()
    command_snake = to_snake_case(command_name)

    return CLI_TEST_TEMPLATE.format(
        command_name=command_name,
        command=command,
        Command=command.capitalize()
    )


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Test Code Generator\n")
        print("Usage:")
        print("  helper.py model <ModelClass> [field]")
        print("    Example: helper.py model Task title")
        print()
        print("  helper.py service <ModelClass> <ServiceClass> [field]")
        print("    Example: helper.py service Task TaskService title")
        print()
        print("  helper.py cli <CommandName>")
        print("    Example: helper.py cli Add")
        print()
        print("  helper.py all <ModelClass> <ServiceClass> [field]")
        print("    Example: helper.py all Task TaskService title")
        sys.exit(1)

    command = sys.argv[1]

    if command == "model":
        if len(sys.argv) < 3:
            print("L ModelClass required")
            print("Example: helper.py model Task title")
            sys.exit(1)

        model_class = sys.argv[2]
        field = sys.argv[3] if len(sys.argv) > 3 else "title"

        code = generate_model_test(model_class, field)
        print(code)

    elif command == "service":
        if len(sys.argv) < 4:
            print("L ModelClass and ServiceClass required")
            print("Example: helper.py service Task TaskService title")
            sys.exit(1)

        model_class = sys.argv[2]
        service_class = sys.argv[3]
        field = sys.argv[4] if len(sys.argv) > 4 else "title"

        code = generate_service_test(model_class, service_class, field)
        print(code)

    elif command == "cli":
        if len(sys.argv) < 3:
            print("L CommandName required")
            print("Example: helper.py cli Add")
            sys.exit(1)

        command_name = sys.argv[2]

        code = generate_cli_test(command_name)
        print(code)

    elif command == "all":
        if len(sys.argv) < 4:
            print("L ModelClass and ServiceClass required")
            print("Example: helper.py all Task TaskService title")
            sys.exit(1)

        model_class = sys.argv[2]
        service_class = sys.argv[3]
        field = sys.argv[4] if len(sys.argv) > 4 else "title"

        print("=" * 60)
        print(f"MODEL TEST: test_{to_snake_case(model_class)}.py")
        print("=" * 60)
        print(generate_model_test(model_class, field))

        print("\n" + "=" * 60)
        print(f"SERVICE TEST: test_{to_snake_case(service_class)}.py")
        print("=" * 60)
        print(generate_service_test(model_class, service_class, field))

    else:
        print(f"L Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
