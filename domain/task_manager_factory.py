#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Factory para criar gerenciadores de tarefas de diferentes tipos.
"""

import logging
from typing import Optional, Dict, Any, Type

# Importação da interface base para TaskManager
from arcee_cli.domain.task_manager_interface import TaskManagerInterface
# Importação do gerenciador TESS consolidado
from arcee_cli.domain.tess_manager_consolidated import TessManager

logger = logging.getLogger(__name__)

class TaskManagerFactory:
    """
    Factory para criar gerenciadores de tarefas para diferentes provedores.
    """
    
    @staticmethod
    def create(provider: str, **kwargs) -> Optional[TaskManagerInterface]:
        """
        Cria um gerenciador de tarefas para o provedor especificado.
        
        Args:
            provider: Nome do provedor (ex: "arcee", "agno")
            **kwargs: Argumentos adicionais para o gerenciador
            
        Returns:
            Gerenciador de tarefas ou None se o provedor não for suportado
        """
        logger.info(f"Criando gerenciador de tarefas para provedor: {provider}")
        
        if provider.lower() == "agno":
            try:
                # Cria uma instância do TessManager com os parâmetros fornecidos
                api_key = kwargs.get("api_key")
                api_url = kwargs.get("api_url")
                session_id = kwargs.get("session_id")
                
                logger.info(f"Inicializando TessManager com sessão {session_id}")
                manager = TessManager(api_key=api_key, api_url=api_url, session_id=session_id)
                logger.info("TessManager inicializado com sucesso")
                return manager
            except Exception as e:
                logger.error(f"Erro ao criar gerenciador TESS: {e}")
                return None
                
        # Adicione outros provedores conforme necessário
        
        logger.warning(f"Provedor não suportado: {provider}")
        return None 