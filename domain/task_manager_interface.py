#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface para gerenciadores de tarefas

Define a interface comum que todos os gerenciadores de tarefas devem implementar.
Isso permite trocar facilmente entre diferentes sistemas (Tess, MCP, etc.)
sem precisar modificar o código cliente.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class TaskManagerInterface(ABC):
    """Interface abstrata para gerenciadores de tarefas"""
    
    @abstractmethod
    def get_boards(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de quadros/projetos disponíveis
        
        Returns:
            Lista de quadros/projetos como dicionários
        """
        pass
    
    @abstractmethod
    def get_lists(self, board_id: str) -> List[Dict[str, Any]]:
        """
        Obtém as listas/colunas de um quadro/projeto
        
        Args:
            board_id: ID do quadro/projeto
            
        Returns:
            Lista de listas/colunas como dicionários
        """
        pass
    
    @abstractmethod
    def get_cards(self, list_id: str) -> List[Dict[str, Any]]:
        """
        Obtém os cartões/tarefas de uma lista/coluna
        
        Args:
            list_id: ID da lista/coluna
            
        Returns:
            Lista de cartões/tarefas como dicionários
        """
        pass
    
    @abstractmethod
    def create_board(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Cria um novo quadro/projeto
        
        Args:
            name: Nome do quadro/projeto
            description: Descrição opcional
            
        Returns:
            Dados do quadro/projeto criado
        """
        pass
    
    @abstractmethod
    def create_list(self, board_id: str, name: str) -> Dict[str, Any]:
        """
        Cria uma nova lista/coluna em um quadro/projeto
        
        Args:
            board_id: ID do quadro/projeto
            name: Nome da lista/coluna
            
        Returns:
            Dados da lista/coluna criada
        """
        pass
    
    @abstractmethod
    def create_card(self, list_id: str, name: str, description: Optional[str] = None, 
                    due_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Cria um novo cartão/tarefa em uma lista/coluna
        
        Args:
            list_id: ID da lista/coluna
            name: Nome do cartão/tarefa
            description: Descrição opcional
            due_date: Data de vencimento opcional
            
        Returns:
            Dados do cartão/tarefa criado
        """
        pass
    
    @abstractmethod
    def archive_card(self, card_id: str) -> Dict[str, Any]:
        """
        Arquiva/remove um cartão/tarefa
        
        Args:
            card_id: ID do cartão/tarefa
            
        Returns:
            Dados do cartão/tarefa arquivado
        """
        pass
    
    @abstractmethod
    def delete_board(self, board_id: str) -> Dict[str, Any]:
        """
        Exclui um quadro/projeto
        
        Args:
            board_id: ID do quadro/projeto
            
        Returns:
            Dados do quadro/projeto excluído
        """
        pass
    
    @abstractmethod
    def search_cards(self, query: str, board_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Busca cartões/tarefas por texto
        
        Args:
            query: Texto para busca
            board_id: ID do quadro/projeto opcional para limitar a busca
            
        Returns:
            Lista de cartões/tarefas encontrados
        """
        pass
    
    @abstractmethod
    def get_activity(self, board_id: Optional[str] = None, card_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém atividades recentes
        
        Args:
            board_id: ID do quadro/projeto opcional
            card_id: ID do cartão/tarefa opcional
            
        Returns:
            Lista de atividades
        """
        pass
    
    @property
    @abstractmethod
    def manager_name(self) -> str:
        """
        Nome do gerenciador de tarefas
        
        Returns:
            Nome do gerenciador (ex: "Tess", "Airtable", etc.)
        """
        pass 