#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API para comunicação com o servidor TESS MCP.

Este módulo fornece as funções para comunicação com o servidor TESS MCP,
que implementa a API para gerenciamento de tarefas.
"""

import os
import json
import logging
import requests
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)

class TessAPI:
    """API para comunicação com o servidor TESS MCP"""
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Inicializa a API TESS
        
        Args:
            base_url: URL base do servidor TESS (opcional, padrão: usa variável de ambiente TESS_API_URL)
            api_key: Chave de API (opcional, padrão: usa variável de ambiente TESS_API_KEY)
        """
        self.base_url = base_url or os.environ.get("TESS_API_URL", "http://localhost:5000/api")
        self.api_key = api_key or os.environ.get("TESS_API_KEY")
        self.session = requests.Session()
        
        # Define headers padrão
        self.headers = {}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Realiza uma requisição HTTP para o servidor TESS
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint da API
            data: Dados a serem enviados (opcional)
            
        Returns:
            Resposta do servidor
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=self.headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=self.headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=self.headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=self.headers)
            else:
                return {"error": f"Método HTTP não suportado: {method}"}
            
            # Verifica se a resposta foi bem-sucedida
            if response.status_code >= 400:
                error_msg = ""
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", str(response.status_code))
                except:
                    error_msg = response.text or str(response.status_code)
                
                return {"error": f"Erro na requisição: {error_msg}"}
            
            # Tenta extrair os dados JSON
            try:
                return response.json()
            except:
                return {"data": response.text}
        
        except requests.RequestException as e:
            logger.exception(f"Erro na requisição para {url}: {str(e)}")
            return {"error": f"Erro na comunicação com o servidor: {str(e)}"}
    
    def health_check(self) -> bool:
        """
        Verifica se o servidor está disponível
        
        Returns:
            True se o servidor estiver disponível, False caso contrário
        """
        try:
            response = self._make_request("GET", "/health")
            return "error" not in response
        except:
            return False
    
    def get_boards(self) -> List[Dict[str, Any]]:
        """
        Obtém todos os quadros disponíveis
        
        Returns:
            Lista de quadros
        """
        response = self._make_request("GET", "/boards")
        
        if "error" in response:
            logger.error(f"Erro ao obter quadros: {response['error']}")
            return []
        
        return response.get("boards", [])
    
    def get_board(self, board_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações de um quadro específico
        
        Args:
            board_id: ID do quadro
            
        Returns:
            Dados do quadro ou None se não encontrado
        """
        response = self._make_request("GET", f"/boards/{board_id}")
        
        if "error" in response:
            logger.error(f"Erro ao obter quadro {board_id}: {response['error']}")
            return None
        
        return response.get("board")
    
    def create_board(self, name: str, description: str = "") -> Dict[str, Any]:
        """
        Cria um novo quadro
        
        Args:
            name: Nome do quadro
            description: Descrição do quadro (opcional)
            
        Returns:
            Dados do quadro criado ou erro
        """
        data = {
            "name": name,
            "description": description
        }
        
        return self._make_request("POST", "/boards", data)
    
    def update_board(self, board_id: str, name: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Atualiza um quadro existente
        
        Args:
            board_id: ID do quadro
            name: Novo nome do quadro (opcional)
            description: Nova descrição do quadro (opcional)
            
        Returns:
            Dados do quadro atualizado ou erro
        """
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        
        return self._make_request("PUT", f"/boards/{board_id}", data)
    
    def delete_board(self, board_id: str) -> Dict[str, Any]:
        """
        Exclui um quadro
        
        Args:
            board_id: ID do quadro
            
        Returns:
            Resultado da operação ou erro
        """
        return self._make_request("DELETE", f"/boards/{board_id}")
    
    def get_lists(self, board_id: str) -> List[Dict[str, Any]]:
        """
        Obtém todas as listas de um quadro
        
        Args:
            board_id: ID do quadro
            
        Returns:
            Lista de listas
        """
        response = self._make_request("GET", f"/boards/{board_id}/lists")
        
        if "error" in response:
            logger.error(f"Erro ao obter listas do quadro {board_id}: {response['error']}")
            return []
        
        return response.get("lists", [])
    
    def get_list(self, list_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações de uma lista específica
        
        Args:
            list_id: ID da lista
            
        Returns:
            Dados da lista ou None se não encontrada
        """
        response = self._make_request("GET", f"/lists/{list_id}")
        
        if "error" in response:
            logger.error(f"Erro ao obter lista {list_id}: {response['error']}")
            return None
        
        return response.get("list")
    
    def create_list(self, board_id: str, name: str) -> Dict[str, Any]:
        """
        Cria uma nova lista em um quadro
        
        Args:
            board_id: ID do quadro
            name: Nome da lista
            
        Returns:
            Dados da lista criada ou erro
        """
        data = {
            "name": name
        }
        
        return self._make_request("POST", f"/boards/{board_id}/lists", data)
    
    def update_list(self, list_id: str, name: Optional[str] = None, position: Optional[int] = None) -> Dict[str, Any]:
        """
        Atualiza uma lista existente
        
        Args:
            list_id: ID da lista
            name: Novo nome da lista (opcional)
            position: Nova posição da lista (opcional)
            
        Returns:
            Dados da lista atualizada ou erro
        """
        data = {}
        if name is not None:
            data["name"] = name
        if position is not None:
            data["position"] = position
        
        return self._make_request("PUT", f"/lists/{list_id}", data)
    
    def delete_list(self, list_id: str) -> Dict[str, Any]:
        """
        Exclui uma lista
        
        Args:
            list_id: ID da lista
            
        Returns:
            Resultado da operação ou erro
        """
        return self._make_request("DELETE", f"/lists/{list_id}")
    
    def get_cards(self, list_id: str) -> List[Dict[str, Any]]:
        """
        Obtém todos os cards de uma lista
        
        Args:
            list_id: ID da lista
            
        Returns:
            Lista de cards
        """
        response = self._make_request("GET", f"/lists/{list_id}/cards")
        
        if "error" in response:
            logger.error(f"Erro ao obter cards da lista {list_id}: {response['error']}")
            return []
        
        return response.get("cards", [])
    
    def get_card(self, card_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações de um card específico
        
        Args:
            card_id: ID do card
            
        Returns:
            Dados do card ou None se não encontrado
        """
        response = self._make_request("GET", f"/cards/{card_id}")
        
        if "error" in response:
            logger.error(f"Erro ao obter card {card_id}: {response['error']}")
            return None
        
        return response.get("card")
    
    def create_card(self, list_id: str, name: str, description: str = "", due_date: str = "") -> Dict[str, Any]:
        """
        Cria um novo card em uma lista
        
        Args:
            list_id: ID da lista
            name: Nome do card
            description: Descrição do card (opcional)
            due_date: Data de vencimento (opcional, formato: YYYY-MM-DD)
            
        Returns:
            Dados do card criado ou erro
        """
        data = {
            "name": name,
            "description": description
        }
        
        if due_date:
            data["due_date"] = due_date
        
        return self._make_request("POST", f"/lists/{list_id}/cards", data)
    
    def update_card(self, card_id: str, **kwargs) -> Dict[str, Any]:
        """
        Atualiza um card existente
        
        Args:
            card_id: ID do card
            **kwargs: Campos a serem atualizados (name, description, due_date, etc.)
            
        Returns:
            Dados do card atualizado ou erro
        """
        return self._make_request("PUT", f"/cards/{card_id}", kwargs)
    
    def archive_card(self, card_id: str) -> Dict[str, Any]:
        """
        Arquiva um card
        
        Args:
            card_id: ID do card
            
        Returns:
            Resultado da operação ou erro
        """
        return self.update_card(card_id, archived=True)
    
    def delete_card(self, card_id: str) -> Dict[str, Any]:
        """
        Exclui um card
        
        Args:
            card_id: ID do card
            
        Returns:
            Resultado da operação ou erro
        """
        return self._make_request("DELETE", f"/cards/{card_id}")
    
    def search_cards(self, query: str, board_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Busca cards por texto
        
        Args:
            query: Texto a ser buscado
            board_id: ID do quadro para limitar a busca (opcional)
            
        Returns:
            Lista de cards encontrados
        """
        endpoint = "/cards/search"
        if board_id:
            endpoint += f"?board_id={board_id}"
        
        response = self._make_request("GET", f"{endpoint}&query={query}" if board_id else f"{endpoint}?query={query}")
        
        if "error" in response:
            logger.error(f"Erro ao buscar cards com termo '{query}': {response['error']}")
            return []
        
        return response.get("cards", []) 