#!/usr/bin/env python3
"""
Model & Service Code Generator

Generate boilerplate code for dataclass models and service classes.
"""

import sys
from pathlib import Path
from typing import List, Optional


# Template for dataclass model
MODEL_TEMPLATE = '''"""
{description}
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Set
from src.models.exceptions import ValidationError


@dataclass
class {class_name}:
    """{description}."""

    # Required fields
    id: int
    {required_fields}

    # Optional fields
    {optional_fields}

    def __post_init__(self) -> None:
        """Validate on initialization."""
        {validations}

{validation_methods}
'''

# Template for service class
SERVICE_TEMPLATE = '''"""
{description}
"""

from typing import List, Optional
from src.models.{model_file} import {model_class}
from src.models.exceptions import {model_class}NotFoundError, ValidationError
from src.storage.in_memory_store import {model_class}Store
from src.lib.id_generator import IdGenerator


class {service_class}:
    """{description}."""

    def __init__(
        self,
        store: {model_class}Store,
        id_gen: IdGenerator
    ) -> None:
        self._store = store
        self._id_gen = id_gen

    def add(
        self,
        {add_params}
    ) -> {model_class}:
        """
        Create a new {model_name}.

        Args:
            {add_args_docs}

        Returns:
            Created {model_class} instance

        Raises:
            ValidationError: If input validation fails
        """
        {model_var} = {model_class}(
            id=self._id_gen.next(),
            {model_init_params}
        )
        self._store.save({model_var})
        return {model_var}

    def get(self, {model_var}_id: int) -> {model_class}:
        """
        Retrieve {model_name} by ID.

        Args:
            {model_var}_id: {model_class} ID

        Returns:
            {model_class} instance

        Raises:
            {model_class}NotFoundError: If {model_name} doesn't exist
        """
        {model_var} = self._store.get({model_var}_id)
        if not {model_var}:
            raise {model_class}NotFoundError(f"{model_class} #{{ {model_var}_id}} not found")
        return {model_var}

    def all(self) -> List[{model_class}]:
        """Get all {model_plural} sorted by ID."""
        return sorted(self._store.all(), key=lambda t: t.id)

    def update(
        self,
        {model_var}_id: int,
        {update_params}
    ) -> {model_class}:
        """
        Update {model_name} fields.

        Args:
            {model_var}_id: {model_class} ID
            {update_args_docs}

        Returns:
            Updated {model_class} instance

        Raises:
            {model_class}NotFoundError: If {model_name} doesn't exist
            ValidationError: If new values invalid
        """
        {model_var} = self.get({model_var}_id)

        updated = {model_class}(
            id={model_var}.id,
            {update_init_params}
        )

        self._store.save(updated)
        return updated

    def delete(self, {model_var}_id: int) -> None:
        """
        Delete {model_name}.

        Args:
            {model_var}_id: {model_class} ID

        Raises:
            {model_class}NotFoundError: If {model_name} doesn't exist
        """
        {model_var} = self.get({model_var}_id)
        self._store.delete({model_var}_id)
'''

# Template for storage class
STORE_TEMPLATE = '''"""
In-memory storage for {model_class}.
"""

from typing import Dict, List, Optional
from src.models.{model_file} import {model_class}


class InMemory{model_class}Store:
    """In-memory {model_name} storage."""

    def __init__(self) -> None:
        self._{model_var}s: Dict[int, {model_class}] = {{}}

    def save(self, {model_var}: {model_class}) -> None:
        """Save or update {model_name}."""
        self._{model_var}s[{model_var}.id] = {model_var}

    def get(self, {model_var}_id: int) -> Optional[{model_class}]:
        """Get {model_name} by ID."""
        return self._{model_var}s.get({model_var}_id)

    def all(self) -> List[{model_class}]:
        """Get all {model_plural}."""
        return list(self._{model_var}s.values())

    def delete(self, {model_var}_id: int) -> None:
        """Delete {model_name}."""
        self._{model_var}s.pop({model_var}_id, None)
'''


def to_snake_case(name: str) -> str:
    """Convert PascalCase to snake_case."""
    result = []
    for i, char in enumerate(name):
        if char.isupper() and i > 0:
            result.append('_')
        result.append(char.lower())
    return ''.join(result)


def generate_model(
    class_name: str,
    description: str,
    required_fields: List[str],
    optional_fields: List[str]
) -> str:
    """Generate dataclass model code."""

    # Format required fields
    req_fields_str = "\n    ".join(required_fields)

    # Format optional fields
    opt_fields_str = "\n    ".join(optional_fields) if optional_fields else "created_at: datetime = field(default_factory=datetime.now)"

    # Generate validation method calls
    validations = "\n        ".join([
        f"self._validate_{field.split(':')[0].strip()}()"
        for field in required_fields
    ])

    # Generate validation methods
    validation_methods = []
    for field in required_fields:
        field_name = field.split(':')[0].strip()
        validation_methods.append(f'''    def _validate_{field_name}(self) -> None:
        """Validate {field_name}."""
        # TODO: Add validation logic
        pass
''')

    validation_methods_str = "\n".join(validation_methods)

    return MODEL_TEMPLATE.format(
        class_name=class_name,
        description=description,
        required_fields=req_fields_str,
        optional_fields=opt_fields_str,
        validations=validations,
        validation_methods=validation_methods_str
    )


def generate_service(
    model_class: str,
    description: str,
    fields: List[str]
) -> str:
    """Generate service class code."""

    model_var = to_snake_case(model_class)
    model_file = model_var
    model_name = model_class.lower()
    model_plural = model_name + "s"

    # Parse fields for add method
    add_params_list = []
    add_args_docs_list = []
    model_init_params_list = []

    for field in fields:
        field_name = field.split(':')[0].strip()
        field_type = field.split(':')[1].strip() if ':' in field else 'str'

        add_params_list.append(f"{field_name}: {field_type}")
        add_args_docs_list.append(f"{field_name}: {field_name.replace('_', ' ').capitalize()}")
        model_init_params_list.append(f"{field_name}={field_name}")

    add_params = ",\n        ".join(add_params_list)
    add_args_docs = "\n            ".join(add_args_docs_list)
    model_init_params = ",\n            ".join(model_init_params_list)

    # For update method (all optional)
    update_params_list = [f"{f.split(':')[0].strip()}: Optional[{f.split(':')[1].strip() if ':' in f else 'str'}] = None" for f in fields]
    update_params = ",\n        ".join(update_params_list)
    update_args_docs = "\n            ".join([f"{f.split(':')[0].strip()}: New {f.split(':')[0].strip()} (None = keep current)" for f in fields])

    # For update init params
    update_init_list = []
    for field in fields:
        field_name = field.split(':')[0].strip()
        update_init_list.append(f"{field_name}={field_name} if {field_name} is not None else {model_var}.{field_name}")

    update_init_params = ",\n            ".join(update_init_list)

    return SERVICE_TEMPLATE.format(
        description=description,
        model_file=model_file,
        model_class=model_class,
        service_class=f"{model_class}Service",
        model_var=model_var,
        model_name=model_name,
        model_plural=model_plural,
        add_params=add_params,
        add_args_docs=add_args_docs,
        model_init_params=model_init_params,
        update_params=update_params,
        update_args_docs=update_args_docs,
        update_init_params=update_init_params
    )


def generate_store(model_class: str) -> str:
    """Generate in-memory store class code."""

    model_var = to_snake_case(model_class)
    model_file = model_var
    model_name = model_class.lower()
    model_plural = model_name + "s"

    return STORE_TEMPLATE.format(
        model_class=model_class,
        model_file=model_file,
        model_var=model_var,
        model_name=model_name,
        model_plural=model_plural
    )


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Model & Service Code Generator\n")
        print("Usage:")
        print("  helper.py model <ClassName> <description>")
        print("    Example: helper.py model Task 'Represents a todo task'")
        print()
        print("  helper.py service <ModelClass> <description>")
        print("    Example: helper.py service Task 'Task management service'")
        print()
        print("  helper.py store <ModelClass>")
        print("    Example: helper.py store Task")
        print()
        print("  helper.py all <ModelClass> <description>")
        print("    Example: helper.py all Task 'Todo task management'")
        sys.exit(1)

    command = sys.argv[1]

    if command == "model":
        if len(sys.argv) < 4:
            print("L ClassName and description required")
            print("Example: helper.py model Task 'Represents a todo task'")
            sys.exit(1)

        class_name = sys.argv[2]
        description = sys.argv[3]

        # Example fields (customize as needed)
        required_fields = ["title: str"]
        optional_fields = ["description: Optional[str] = None"]

        code = generate_model(class_name, description, required_fields, optional_fields)
        print(code)

    elif command == "service":
        if len(sys.argv) < 4:
            print("L ModelClass and description required")
            print("Example: helper.py service Task 'Task management service'")
            sys.exit(1)

        model_class = sys.argv[2]
        description = sys.argv[3]

        # Example fields
        fields = ["title: str", "description: Optional[str]"]

        code = generate_service(model_class, description, fields)
        print(code)

    elif command == "store":
        if len(sys.argv) < 3:
            print("L ModelClass required")
            print("Example: helper.py store Task")
            sys.exit(1)

        model_class = sys.argv[2]
        code = generate_store(model_class)
        print(code)

    elif command == "all":
        if len(sys.argv) < 4:
            print("L ModelClass and description required")
            print("Example: helper.py all Task 'Todo task management'")
            sys.exit(1)

        model_class = sys.argv[2]
        description = sys.argv[3]

        print("=" * 60)
        print(f"MODEL: {model_class}")
        print("=" * 60)
        required_fields = ["title: str"]
        optional_fields = ["description: Optional[str] = None"]
        print(generate_model(model_class, description, required_fields, optional_fields))

        print("\n" + "=" * 60)
        print(f"SERVICE: {model_class}Service")
        print("=" * 60)
        fields = ["title: str", "description: Optional[str]"]
        print(generate_service(model_class, description, fields))

        print("\n" + "=" * 60)
        print(f"STORE: InMemory{model_class}Store")
        print("=" * 60)
        print(generate_store(model_class))

    else:
        print(f"L Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
