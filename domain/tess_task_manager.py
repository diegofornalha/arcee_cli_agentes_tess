#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AVISO: Este arquivo está DEPRECIADO.
Use a implementação consolidada em tess_manager_consolidated.py.
Este arquivo será removido em versões futuras.
"""

"""
Módulo para gerenciamento de tarefas usando a API TESS
"""
import os
import requests
import json
import logging
from typing import Dict, List, Optional, Any

from arcee_cli.domain.task_manager_interface import TaskManagerInterface

logger = logging.getLogger(__name__)

class TessTaskManager(TaskManagerInterface):
    """
    Gerenciador de tarefas usando a API TESS.
    Fornece interface simplificada para operações da API TESS.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o gerenciador TESS com a chave de API fornecida ou buscando no ambiente.
        
        Args:
            api_key: Chave de API do TESS (opcional, se não fornecida busca no ambiente)
        """
        # Tenta obter a chave da API
        self.api_key = api_key or os.environ.get('TESS_API_KEY')
        if not self.api_key:
            # Tenta encontrar em um arquivo .env na raiz do projeto
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'mcp-server-tess', '.env')
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('TESS_API_KEY='):
                            self.api_key = line.strip().split('=', 1)[1]
                            break
        
        if not self.api_key:
            raise ValueError("Chave de API do TESS não fornecida e não encontrada no ambiente")
        
        self.base_url = "https://tess.pareto.io/api"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Timeout padrão para requisições em segundos
        self.timeout = 120
        
        logger.info("TessTaskManager inicializado com sucesso")
    
    def listar_agentes(self) -> List[Dict[str, Any]]:
        """
        Lista todos os agentes disponíveis na conta TESS.
        
        Returns:
            Lista de agentes com seus detalhes
        """
        url = f"{self.base_url}/agents"
        
        try:
            logger.info("Listando agentes TESS")
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Retorna a lista de agentes
            return response.json().get('data', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao listar agentes: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Status: {e.response.status_code}")
                logger.error(f"Resposta: {e.response.text}")
            return []
    
    def obter_agente(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém os detalhes de um agente específico.
        
        Args:
            agent_id: ID do agente
            
        Returns:
            Detalhes do agente ou None se não encontrado
        """
        url = f"{self.base_url}/agents/{agent_id}"
        
        try:
            logger.info(f"Obtendo detalhes do agente {agent_id}")
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter detalhes do agente {agent_id}: {e}")
            return None
    
    def executar_agente(self, agent_id: str, parametros: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa um agente com os parâmetros fornecidos e retorna o resultado.
        
        Args:
            agent_id: ID do agente
            parametros: Parâmetros para execução do agente (varia por tipo de agente)
            
        Returns:
            Resultado da execução com campos: success, output, error (opcional)
        """
        url = f"{self.base_url}/agents/{agent_id}/execute"
        
        # Garantir que waitExecution é True para obter resultado diretamente
        parametros["waitExecution"] = True
        
        try:
            logger.info(f"Executando agente {agent_id}")
            logger.debug(f"Parâmetros: {json.dumps(parametros)}")
            
            response = requests.post(url, headers=self.headers, json=parametros, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"Resposta recebida: {json.dumps(result)}")
            
            # Extrai o resultado da execução
            if 'responses' in result and len(result['responses']) > 0:
                response_data = result['responses'][0]
                
                # Verifica se a execução foi bem-sucedida e se há saída
                if response_data.get('status') == 'succeeded' and 'output' in response_data:
                    return {
                        'success': True,
                        'output': response_data['output'],
                        'details': response_data
                    }
                else:
                    # Execução não foi concluída ou falhou
                    return {
                        'success': False,
                        'output': None,
                        'error': f"Status da execução: {response_data.get('status', 'desconhecido')}",
                        'details': response_data
                    }
            
            # Caso não encontre respostas válidas
            return {
                'success': False,
                'output': None,
                'error': "Formato de resposta inesperado",
                'details': result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao executar agente {agent_id}: {e}")
            error_details = {}
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                except:
                    error_details = {'status': e.response.status_code, 'text': e.response.text}
            
            return {
                'success': False,
                'output': None,
                'error': str(e),
                'details': error_details
            }
    
    def listar_arquivos(self) -> List[Dict[str, Any]]:
        """
        Lista os arquivos armazenados na conta TESS.
        
        Returns:
            Lista de arquivos com seus detalhes
        """
        url = f"{self.base_url}/files"
        
        try:
            logger.info("Listando arquivos TESS")
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get('data', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao listar arquivos: {e}")
            return []
    
    def vincular_arquivo(self, caminho_arquivo: str, nome_arquivo: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Faz upload de um arquivo para a conta TESS.
        
        Args:
            caminho_arquivo: Caminho local do arquivo a ser enviado
            nome_arquivo: Nome a ser usado para o arquivo no TESS (opcional)
            
        Returns:
            Detalhes do arquivo criado ou None em caso de erro
        """
        if not os.path.exists(caminho_arquivo):
            logger.error(f"Arquivo não encontrado: {caminho_arquivo}")
            return None
        
        url = f"{self.base_url}/files"
        
        # Preparar dados do formulário
        files = {
            'file': (nome_arquivo or os.path.basename(caminho_arquivo), open(caminho_arquivo, 'rb'))
        }
        
        # Remover o header Content-Type para a biblioteca requests definir automaticamente
        headers = self.headers.copy()
        headers.pop('Content-Type', None)
        
        try:
            logger.info(f"Enviando arquivo {caminho_arquivo}")
            response = requests.post(url, headers=headers, files=files, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao vincular arquivo: {e}")
            return None
    
    @property
    def manager_name(self) -> str:
        """
        Nome do gerenciador de tarefas
        
        Returns:
            Nome do gerenciador ("TESS AI")
        """
        return "TESS AI"
    
    def get_boards(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de quadros/projetos disponíveis
        
        Returns:
            Lista vazia, funcionalidade não suportada pelo TESS
        """
        logger.warning("Método get_boards não implementado para TESS")
        return []
    
    def get_lists(self, board_id: str) -> List[Dict[str, Any]]:
        """
        Obtém as listas/colunas de um quadro/projeto
        
        Args:
            board_id: ID do quadro/projeto
            
        Returns:
            Lista vazia, funcionalidade não suportada pelo TESS
        """
        logger.warning(f"Método get_lists não implementado para TESS, board_id: {board_id}")
        return []
    
    def get_cards(self, list_id: str) -> List[Dict[str, Any]]:
        """
        Obtém os cartões/tarefas de uma lista/coluna
        
        Args:
            list_id: ID da lista/coluna
            
        Returns:
            Lista vazia, funcionalidade não suportada pelo TESS
        """
        logger.warning(f"Método get_cards não implementado para TESS, list_id: {list_id}")
        return []
    
    def create_board(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Cria um novo quadro/projeto
        
        Args:
            name: Nome do quadro/projeto
            description: Descrição opcional
            
        Returns:
            Dicionário vazio, funcionalidade não suportada pelo TESS
        """
        logger.warning(f"Método create_board não implementado para TESS, name: {name}")
        return {"error": "Funcionalidade não suportada pelo TESS"}
    
    def create_list(self, board_id: str, name: str) -> Dict[str, Any]:
        """
        Cria uma nova lista/coluna em um quadro/projeto
        
        Args:
            board_id: ID do quadro/projeto
            name: Nome da lista/coluna
            
        Returns:
            Dicionário vazio, funcionalidade não suportada pelo TESS
        """
        logger.warning(f"Método create_list não implementado para TESS, board_id: {board_id}, name: {name}")
        return {"error": "Funcionalidade não suportada pelo TESS"}
    
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
            Dicionário vazio, funcionalidade não suportada pelo TESS
        """
        logger.warning(f"Método create_card não implementado para TESS, list_id: {list_id}, name: {name}")
        return {"error": "Funcionalidade não suportada pelo TESS"}
    
    def archive_card(self, card_id: str) -> Dict[str, Any]:
        """
        Arquiva/remove um cartão/tarefa
        
        Args:
            card_id: ID do cartão/tarefa
            
        Returns:
            Dicionário vazio, funcionalidade não suportada pelo TESS
        """
        logger.warning(f"Método archive_card não implementado para TESS, card_id: {card_id}")
        return {"error": "Funcionalidade não suportada pelo TESS"}
    
    def delete_board(self, board_id: str) -> Dict[str, Any]:
        """
        Exclui um quadro/projeto
        
        Args:
            board_id: ID do quadro/projeto
            
        Returns:
            Dicionário vazio, funcionalidade não suportada pelo TESS
        """
        logger.warning(f"Método delete_board não implementado para TESS, board_id: {board_id}")
        return {"error": "Funcionalidade não suportada pelo TESS"}
    
    def search_cards(self, query: str, board_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Busca cartões/tarefas por texto
        
        Args:
            query: Texto para busca
            board_id: ID do quadro/projeto opcional para limitar a busca
            
        Returns:
            Lista vazia, funcionalidade não suportada pelo TESS
        """
        logger.warning(f"Método search_cards não implementado para TESS, query: {query}")
        return []
    
    def get_activity(self, board_id: Optional[str] = None, card_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém atividades recentes
        
        Args:
            board_id: ID do quadro/projeto opcional
            card_id: ID do cartão/tarefa opcional
            
        Returns:
            Lista vazia, funcionalidade não suportada pelo TESS
        """
        logger.warning(f"Método get_activity não implementado para TESS")
        return [] 