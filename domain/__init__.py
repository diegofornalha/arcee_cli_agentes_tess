"""
Módulo de domínio da aplicação Arcee CLI.

Define as interfaces e implementações de gerenciadores de tarefas.
"""

from arcee_cli.domain.task_manager_interface import TaskManagerInterface
from arcee_cli.domain.tess_manager_consolidated import TessManager
from arcee_cli.domain.task_manager_factory import TaskManagerFactory

__all__ = [
    "TaskManagerInterface",
    "TessManager",
    "TaskManagerFactory"
] 