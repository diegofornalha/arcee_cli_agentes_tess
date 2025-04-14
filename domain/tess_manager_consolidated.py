#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gerenciador de tarefas TESS consolidado

Este módulo implementa um gerenciador de tarefas para o serviço TESS,
consolidando as funcionalidades dos gerenciadores existentes em uma
única implementação coesa.
"""

import os
import json
import logging
import requests
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from arcee_cli.domain.task_manager_interface import TaskManagerInterface
from arcee_cli.domain.exceptions import (
    TessError, TessAgentExecutionError, TessFileError,
    ConfigurationError, APIError, ResourceNotFoundError
)

logger = logging.getLogger(__name__)

class TessManager(TaskManagerInterface):
    """
    Gerenciador consolidado para o serviço TESS.
    
    Esta classe implementa a interface TaskManagerInterface e fornece
    funcionalidades para interagir com o serviço TESS de forma unificada.
    """
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None, session_id: Optional[str] = None):
        """
        Inicializa o gerenciador TESS.
        
        Args:
            api_key: Chave da API TESS (opcional)
            api_url: URL base da API TESS (opcional)
            session_id: ID de sessão MCP (opcional)
            
        Raises:
            ConfigurationError: Quando a chave API não está disponível
        """
        # Configuração da API
        self.api_key = api_key or os.environ.get('TESS_API_KEY')
        
        # Se não foi fornecido na variável de ambiente, tenta buscar no arquivo .env
        if not self.api_key:
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'mcp-server-agno', '.env')
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('TESS_API_KEY='):
                            self.api_key = line.strip().split('=', 1)[1]
                            break
        
        if not self.api_key:
            raise ConfigurationError("Chave de API do TESS não fornecida e não encontrada no ambiente")
        
        self.base_url = api_url or "https://agno.pareto.io/api"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Configuração para MCP (quando aplicável)
        self.session_id = session_id
        
        # Timeout padrão para requisições em segundos
        self.timeout = 120
        
        # Cache para requisições frequentes
        self.cache = {}
        self.cache_ttl = 60  # segundos
        
        logger.info("TessManager inicializado com sucesso")
    
    @property
    def manager_name(self) -> str:
        """
        Nome do gerenciador de tarefas
        
        Returns:
            Nome do gerenciador ("TESS AI")
        """
        return "TESS AI"
    
    # ------------------- Métodos específicos TESS -------------------
    
    def listar_agentes(self) -> List[Dict[str, Any]]:
        """
        Lista todos os agentes disponíveis na conta TESS.
        
        Returns:
            Lista de agentes com seus detalhes
            
        Raises:
            APIError: Quando ocorre um erro na comunicação com a API
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
            status_code = None
            details = {}
            
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                logger.error(f"Status: {status_code}")
                logger.error(f"Resposta: {e.response.text}")
                try:
                    details = e.response.json()
                except:
                    details = {"text": e.response.text}
            
            raise APIError(
                f"Erro ao listar agentes TESS: {str(e)}", 
                status_code=status_code, 
                details=details
            ) from e
        except Exception as e:
            logger.error(f"Erro inesperado ao listar agentes: {e}")
            # Em caso de erro inesperado, retornamos lista vazia para não quebrar o fluxo
            return []
    
    def obter_agente(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém os detalhes de um agente específico.
        
        Args:
            agent_id: ID do agente
            
        Returns:
            Detalhes do agente ou None se não encontrado
            
        Raises:
            ResourceNotFoundError: Quando o agente não é encontrado
            APIError: Quando ocorre um erro na comunicação com a API
        """
        url = f"{self.base_url}/agents/{agent_id}"
        
        try:
            logger.info(f"Obtendo detalhes do agente {agent_id}")
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 404:
                raise ResourceNotFoundError(f"Agente com ID '{agent_id}' não encontrado")
                
            response.raise_for_status()
            return response.json()
        except ResourceNotFoundError:
            # Propagamos a exceção de recurso não encontrado
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter detalhes do agente {agent_id}: {e}")
            status_code = None
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
            
            raise APIError(
                f"Erro ao obter agente TESS: {str(e)}", 
                status_code=status_code
            ) from e
        except Exception as e:
            logger.error(f"Erro inesperado ao obter agente: {e}")
            return None
    
    def executar_agente(self, agent_id: str, parametros: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa um agente com os parâmetros fornecidos e retorna o resultado.
        
        Args:
            agent_id: ID do agente
            parametros: Parâmetros para execução do agente (varia por tipo de agente)
            
        Returns:
            Resultado da execução com campos: success, output, error (opcional)
            
        Raises:
            ResourceNotFoundError: Quando o agente não é encontrado
            TessAgentExecutionError: Quando ocorre um erro na execução do agente
            APIError: Quando ocorre um erro na comunicação com a API
        """
        url = f"{self.base_url}/agents/{agent_id}/execute"
        
        # Garantir que waitExecution é True para obter resultado diretamente
        parametros_execucao = parametros.copy()
        parametros_execucao["waitExecution"] = True
        
        try:
            logger.info(f"Executando agente {agent_id}")
            logger.debug(f"Parâmetros: {json.dumps(parametros_execucao)}")
            
            response = requests.post(url, headers=self.headers, json=parametros_execucao, timeout=self.timeout)
            
            if response.status_code == 404:
                raise ResourceNotFoundError(f"Agente com ID '{agent_id}' não encontrado")
                
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
                    error_msg = f"Status da execução: {response_data.get('status', 'desconhecido')}"
                    
                    # Retornamos falha com detalhes, mas não lançamos exceção para manter compatibilidade
                    return {
                        'success': False,
                        'output': None,
                        'error': error_msg,
                        'details': response_data
                    }
            
            # Caso não encontre respostas válidas
            return {
                'success': False,
                'output': None,
                'error': "Formato de resposta inesperado",
                'details': result
            }
            
        except ResourceNotFoundError:
            # Propagamos a exceção de recurso não encontrado
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao executar agente {agent_id}: {e}")
            error_details = {}
            status_code = None
            
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                try:
                    error_details = e.response.json()
                except:
                    error_details = {'status': e.response.status_code, 'text': e.response.text}
            
            # Para manter a compatibilidade, retornamos falha ao invés de lançar exceção
            return {
                'success': False,
                'output': None,
                'error': str(e),
                'details': error_details
            }
        except Exception as e:
            logger.error(f"Erro inesperado ao executar agente: {e}")
            # Para manter a compatibilidade, retornamos falha ao invés de lançar exceção
            return {
                'success': False,
                'output': None,
                'error': f"Erro inesperado: {str(e)}",
                'details': {}
            }
    
    def listar_arquivos(self) -> List[Dict[str, Any]]:
        """
        Lista os arquivos armazenados na conta TESS.
        
        Returns:
            Lista de arquivos com seus detalhes
            
        Raises:
            APIError: Quando ocorre um erro na comunicação com a API
        """
        url = f"{self.base_url}/files"
        
        try:
            logger.info("Listando arquivos TESS")
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get('data', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao listar arquivos: {e}")
            status_code = None
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
            
            raise APIError(
                f"Erro ao listar arquivos TESS: {str(e)}", 
                status_code=status_code
            ) from e
        except Exception as e:
            logger.error(f"Erro inesperado ao listar arquivos: {e}")
            # Em caso de erro inesperado, retornamos lista vazia para não quebrar o fluxo
            return []
    
    def listar_arquivos_agente(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        Lista os arquivos vinculados a um agente específico.
        
        Args:
            agent_id: ID do agente
            
        Returns:
            Lista de arquivos vinculados ao agente
            
        Raises:
            ResourceNotFoundError: Quando o agente não é encontrado
            APIError: Quando ocorre um erro na comunicação com a API
        """
        url = f"{self.base_url}/agents/{agent_id}/files"
        
        try:
            logger.info(f"Listando arquivos do agente {agent_id}")
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 404:
                raise ResourceNotFoundError(f"Agente com ID '{agent_id}' não encontrado")
                
            response.raise_for_status()
            return response.json().get('data', [])
        except ResourceNotFoundError:
            # Propagamos a exceção de recurso não encontrado
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao listar arquivos do agente {agent_id}: {e}")
            status_code = None
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
            
            raise APIError(
                f"Erro ao listar arquivos do agente TESS: {str(e)}", 
                status_code=status_code
            ) from e
        except Exception as e:
            logger.error(f"Erro inesperado ao listar arquivos do agente: {e}")
            # Em caso de erro inesperado, retornamos lista vazia para não quebrar o fluxo
            return []
    
    def vincular_arquivo(self, caminho_arquivo: str, nome_arquivo: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Faz upload de um arquivo para a conta TESS.
        
        Args:
            caminho_arquivo: Caminho local do arquivo a ser enviado
            nome_arquivo: Nome a ser usado para o arquivo no TESS (opcional)
            
        Returns:
            Detalhes do arquivo criado ou None em caso de erro
            
        Raises:
            TessFileError: Quando o arquivo não existe ou há erro no upload
            APIError: Quando ocorre um erro na comunicação com a API
        """
        if not os.path.exists(caminho_arquivo):
            logger.error(f"Arquivo não encontrado: {caminho_arquivo}")
            raise TessFileError(f"Arquivo não encontrado: {caminho_arquivo}")
        
        url = f"{self.base_url}/files"
        
        try:
            files = {
                'file': (nome_arquivo or os.path.basename(caminho_arquivo), open(caminho_arquivo, 'rb'))
            }
            
            # Remover o header Content-Type para a biblioteca requests definir automaticamente
            headers = self.headers.copy()
            headers.pop('Content-Type', None)
            
            logger.info(f"Enviando arquivo {caminho_arquivo}")
            response = requests.post(url, headers=headers, files=files, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao vincular arquivo: {e}")
            status_code = None
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
            
            raise APIError(
                f"Erro ao vincular arquivo TESS: {str(e)}", 
                status_code=status_code
            ) from e
        except (IOError, OSError) as e:
            # Exceções de E/S que não são RequestException
            # (como erros de permissão de arquivo, etc.)
            logger.error(f"Erro ao ler arquivo {caminho_arquivo}: {e}")
            raise TessFileError(f"Erro ao ler arquivo: {str(e)}") from e
        except Exception as e:
            logger.error(f"Erro inesperado ao vincular arquivo: {e}")
            return None
        finally:
            # Garantir que o arquivo seja fechado
            if 'files' in locals() and 'file' in files:
                try:
                    files['file'][1].close()
                except:
                    pass
    
    def vincular_arquivo_agente(self, agent_id: str, file_id: int) -> Dict[str, Any]:
        """
        Vincula um arquivo a um agente.
        
        Args:
            agent_id: ID do agente
            file_id: ID do arquivo
            
        Returns:
            Resultado da operação
            
        Raises:
            ResourceNotFoundError: Quando o agente ou arquivo não é encontrado
            APIError: Quando ocorre um erro na comunicação com a API
        """
        url = f"{self.base_url}/agents/{agent_id}/files"
        
        try:
            logger.info(f"Vinculando arquivo {file_id} ao agente {agent_id}")
            response = requests.post(
                url, 
                headers=self.headers, 
                json={"fileId": file_id},
                timeout=self.timeout
            )
            
            if response.status_code == 404:
                raise ResourceNotFoundError(f"Agente ou arquivo não encontrado (agente: {agent_id}, arquivo: {file_id})")
                
            response.raise_for_status()
            return {"success": True, "message": "Arquivo vinculado com sucesso"}
        except ResourceNotFoundError:
            # Propagamos a exceção de recurso não encontrado
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao vincular arquivo ao agente: {e}")
            status_code = None
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
            
            raise APIError(
                f"Erro ao vincular arquivo ao agente: {str(e)}", 
                status_code=status_code
            ) from e
        except Exception as e:
            logger.error(f"Erro inesperado ao vincular arquivo ao agente: {e}")
            return {"success": False, "error": str(e)}
    
    def remover_arquivo_agente(self, agent_id: str, file_id: int) -> Dict[str, Any]:
        """
        Remove um arquivo de um agente.
        
        Args:
            agent_id: ID do agente
            file_id: ID do arquivo
            
        Returns:
            Resultado da operação
            
        Raises:
            ResourceNotFoundError: Quando o agente ou arquivo não é encontrado
            APIError: Quando ocorre um erro na comunicação com a API
        """
        url = f"{self.base_url}/agents/{agent_id}/files/{file_id}"
        
        try:
            logger.info(f"Removendo arquivo {file_id} do agente {agent_id}")
            response = requests.delete(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 404:
                raise ResourceNotFoundError(f"Agente ou arquivo não encontrado (agente: {agent_id}, arquivo: {file_id})")
                
            response.raise_for_status()
            return {"success": True, "message": "Arquivo removido com sucesso"}
        except ResourceNotFoundError:
            # Propagamos a exceção de recurso não encontrado
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao remover arquivo do agente: {e}")
            status_code = None
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
            
            raise APIError(
                f"Erro ao remover arquivo do agente: {str(e)}", 
                status_code=status_code
            ) from e
        except Exception as e:
            logger.error(f"Erro inesperado ao remover arquivo do agente: {e}")
            return {"success": False, "error": str(e)}
    
    def processar_arquivo(self, file_id: int) -> Dict[str, Any]:
        """
        Solicita o processamento de um arquivo.
        
        Args:
            file_id: ID do arquivo
            
        Returns:
            Resultado da operação
            
        Raises:
            ResourceNotFoundError: Quando o arquivo não é encontrado
            APIError: Quando ocorre um erro na comunicação com a API
        """
        url = f"{self.base_url}/files/{file_id}/process"
        
        try:
            logger.info(f"Processando arquivo {file_id}")
            response = requests.post(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 404:
                raise ResourceNotFoundError(f"Arquivo com ID '{file_id}' não encontrado")
                
            response.raise_for_status()
            return {"success": True, "message": "Solicitação de processamento enviada com sucesso"}
        except ResourceNotFoundError:
            # Propagamos a exceção de recurso não encontrado
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao processar arquivo: {e}")
            status_code = None
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
            
            raise APIError(
                f"Erro ao processar arquivo: {str(e)}", 
                status_code=status_code
            ) from e
        except Exception as e:
            logger.error(f"Erro inesperado ao processar arquivo: {e}")
            return {"success": False, "error": str(e)}
    
    # ------------------- Métodos da interface TaskManagerInterface -------------------
    
    def get_boards(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de quadros/projetos disponíveis.
        Este método é uma simulação para compatibilidade, não é suportado nativamente pelo TESS.
        
        Returns:
            Lista de quadros/projetos como dicionários
        """
        logger.warning("Método get_boards usado, mas não é suportado nativamente pelo TESS")
        return []
    
    def get_lists(self, board_id: str) -> List[Dict[str, Any]]:
        """
        Obtém as listas/colunas de um quadro/projeto.
        Este método é uma simulação para compatibilidade, não é suportado nativamente pelo TESS.
        
        Args:
            board_id: ID do quadro/projeto
            
        Returns:
            Lista de listas/colunas como dicionários
        """
        logger.warning(f"Método get_lists usado com board_id={board_id}, mas não é suportado nativamente pelo TESS")
        return []
    
    def get_cards(self, list_id: str) -> List[Dict[str, Any]]:
        """
        Obtém os cartões/tarefas de uma lista/coluna.
        Este método é uma simulação para compatibilidade, não é suportado nativamente pelo TESS.
        
        Args:
            list_id: ID da lista/coluna
            
        Returns:
            Lista de cartões/tarefas como dicionários
        """
        logger.warning(f"Método get_cards usado com list_id={list_id}, mas não é suportado nativamente pelo TESS")
        return []
    
    def create_board(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Cria um novo quadro/projeto.
        Este método é uma simulação para compatibilidade, não é suportado nativamente pelo TESS.
        
        Args:
            name: Nome do quadro/projeto
            description: Descrição opcional
            
        Returns:
            Dados do quadro/projeto criado
        """
        logger.warning(f"Método create_board usado com name={name}, mas não é suportado nativamente pelo TESS")
        return {"error": "Funcionalidade não suportada pelo TESS"}
    
    def create_list(self, board_id: str, name: str) -> Dict[str, Any]:
        """
        Cria uma nova lista/coluna em um quadro/projeto.
        Este método é uma simulação para compatibilidade, não é suportado nativamente pelo TESS.
        
        Args:
            board_id: ID do quadro/projeto
            name: Nome da lista/coluna
            
        Returns:
            Dados da lista/coluna criada
        """
        logger.warning(f"Método create_list usado com board_id={board_id}, name={name}, mas não é suportado nativamente pelo TESS")
        return {"error": "Funcionalidade não suportada pelo TESS"}
    
    def create_card(self, list_id: str, name: str, description: Optional[str] = None, 
                    due_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Cria um novo cartão/tarefa em uma lista/coluna.
        Este método é uma simulação para compatibilidade, não é suportado nativamente pelo TESS.
        
        Args:
            list_id: ID da lista/coluna
            name: Nome do cartão/tarefa
            description: Descrição opcional
            due_date: Data de vencimento opcional
            
        Returns:
            Dados do cartão/tarefa criado
        """
        logger.warning(f"Método create_card usado com list_id={list_id}, name={name}, mas não é suportado nativamente pelo TESS")
        return {"error": "Funcionalidade não suportada pelo TESS"}
    
    def archive_card(self, card_id: str) -> Dict[str, Any]:
        """
        Arquiva/remove um cartão/tarefa.
        Este método é uma simulação para compatibilidade, não é suportado nativamente pelo TESS.
        
        Args:
            card_id: ID do cartão/tarefa
            
        Returns:
            Dados do cartão/tarefa arquivado
        """
        logger.warning(f"Método archive_card usado com card_id={card_id}, mas não é suportado nativamente pelo TESS")
        return {"error": "Funcionalidade não suportada pelo TESS"}
    
    def delete_board(self, board_id: str) -> Dict[str, Any]:
        """
        Exclui um quadro/projeto.
        Este método é uma simulação para compatibilidade, não é suportado nativamente pelo TESS.
        
        Args:
            board_id: ID do quadro/projeto
            
        Returns:
            Dados do quadro/projeto excluído
        """
        logger.warning(f"Método delete_board usado com board_id={board_id}, mas não é suportado nativamente pelo TESS")
        return {"error": "Funcionalidade não suportada pelo TESS"}
    
    def search_cards(self, query: str, board_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Busca cartões/tarefas por texto.
        Este método é uma simulação para compatibilidade, não é suportado nativamente pelo TESS.
        
        Args:
            query: Texto para busca
            board_id: ID do quadro/projeto opcional para limitar a busca
            
        Returns:
            Lista de cartões/tarefas encontrados
        """
        logger.warning(f"Método search_cards usado com query={query}, mas não é suportado nativamente pelo TESS")
        return []
    
    def get_activity(self, board_id: Optional[str] = None, card_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém atividades recentes.
        Este método é uma simulação para compatibilidade, não é suportado nativamente pelo TESS.
        
        Args:
            board_id: ID do quadro/projeto opcional
            card_id: ID do cartão/tarefa opcional
            
        Returns:
            Lista de atividades
        """
        logger.warning(f"Método get_activity usado, mas não é suportado nativamente pelo TESS")
        return [] 