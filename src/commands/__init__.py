"""
Módulo de comandos para o CLI Arcee.
"""

from .mcp import main_configurar, main_listar, main_executar
from .chat import arcee_chat

__all__ = ["main_configurar", "main_listar", "main_executar", "arcee_chat"] 