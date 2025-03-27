#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exceções personalizadas para o módulo arcee_cli.
"""

from typing import Dict, Optional, Any, Union

class ArceeError(Exception):
    """Classe base para todas as exceções da Arcee CLI."""
    pass


class ConfigurationError(ArceeError):
    """Erro relacionado à configuração (chaves API ausentes, arquivos de configuração inválidos, etc.)."""
    pass


class AuthenticationError(ArceeError):
    """Erro de autenticação com serviços externos."""
    pass


class APIError(ArceeError):
    """Erro de comunicação com API externa."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        """
        Inicializa exceção de API.
        
        Args:
            message: Mensagem de erro
            status_code: Código de status HTTP (opcional)
            details: Detalhes adicionais do erro (opcional)
        """
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class InvalidInputError(ArceeError):
    """Erro de entrada inválida fornecida pelo usuário."""
    pass


class ResourceNotFoundError(ArceeError):
    """Erro quando um recurso (arquivo, agente, etc.) não é encontrado."""
    pass


class TessError(ArceeError):
    """Classe base para erros relacionados ao TESS."""
    pass


class TessAgentExecutionError(TessError):
    """Erro ocorrido durante execução de agente TESS."""
    
    def __init__(self, message: str, agent_id: Optional[str] = None, execution_details: Optional[Dict[str, Any]] = None):
        """
        Inicializa exceção de execução de agente.
        
        Args:
            message: Mensagem de erro
            agent_id: ID do agente que falhou (opcional)
            execution_details: Detalhes da execução (opcional)
        """
        self.agent_id = agent_id
        self.execution_details = execution_details or {}
        super().__init__(message)


class TessFileError(TessError):
    """Erro relacionado a operações com arquivos no TESS."""
    pass


class MCPError(ArceeError):
    """Erro relacionado ao MCP."""
    pass
    

class CrewError(ArceeError):
    """Erro relacionado ao CrewAI."""
    pass 