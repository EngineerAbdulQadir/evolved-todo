"""Shared dependencies for the application to avoid circular imports."""

from src.lib.id_generator import IdGenerator
from src.services.task_service import TaskService
from src.services.task_store import InMemoryTaskStore

# Initialize shared dependencies (singleton pattern for in-memory storage)
_id_generator = IdGenerator()
_task_store = InMemoryTaskStore()
_task_service = TaskService(store=_task_store, id_gen=_id_generator)


def get_task_service() -> TaskService:
    """
    Get the shared task service instance.

    Returns:
        TaskService instance with in-memory storage
    """
    return _task_service
