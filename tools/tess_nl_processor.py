#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Processador de linguagem natural para comandos do TESS.

Este módulo implementa o processador de comandos em linguagem natural para o TESS,
permitindo a execução de comandos como "listar agentes", "executar um agente", etc.
"""

import re
import os
import json
import logging
import time

from typing import Dict, List, Any, Optional, Union, Tuple, Pattern

from arcee_cli.domain.task_manager_factory import TaskManagerFactory
from arcee_cli.domain.tess_task_manager import TessTaskManager

logger = logging.getLogger(__name__)

class TessNLProcessor:
    """Processador de linguagem natural para comandos do TESS"""
    
    def __init__(self, session_id=None):
        """
        Inicializa o processador de linguagem natural
        
        Args:
            session_id: ID opcional da sessão MCP
        """
        # Padrões de comando para diferentes ações
        self.command_patterns = {
            # Padrões para listar agentes
            "listar_agentes": [
                r"(?:lista(?:r)?|mostr(?:a|e|ar)|exib(?:a|e|ir)) (?:os |todos os |meus )?agentes",
                r"quais (?:são )?(?:os |meus )?agentes",
                r"ver (?:os |meus )?agentes"
            ],
            
            # Padrões para obter detalhes de um agente
            "obter_agente": [
                r"(?:obter|mostrar|exibir|detalhar|ver)(?: detalhes)?(?: do| sobre o)? agente [\"']?([^\"']+)[\"']?",
                r"(?:detalhes|informações)(?: do| sobre o)? agente [\"']?([^\"']+)[\"']?"
            ],
            
            # Padrões para executar um agente
            "executar_agente": [
                r"(?:execut(?:a|e|ar)|rodar?|iniciar?)(?: o)? agente [\"']?([^\"']+)[\"']?(?: com(?: a)? mensagem [\"']?([^\"']+)[\"']?)?",
                r"(?:usar|chamar)(?: o)? agente [\"']?([^\"']+)[\"']?(?: com(?: a)? mensagem [\"']?([^\"']+)[\"']?)?"
            ],
            
            # Padrões para listar arquivos
            "listar_arquivos": [
                r"(?:lista(?:r)?|mostr(?:a|e|ar)|exib(?:a|e|ir)) (?:os |todos os |meus )?arquivos",
                r"quais (?:são )?(?:os |meus )?arquivos",
                r"ver (?:os |meus )?arquivos"
            ],
            
            # Padrões para vincular arquivo a um agente
            "vincular_arquivo": [
                r"(?:vincul(?:a|e|ar)|associar|ligar)(?: o)? arquivo [\"']?([^\"']+)[\"']?(?: (?:ao|com o|no)(?: agente)? [\"']?([^\"']+)[\"']?)?",
                r"(?:adicionar?)(?: o)? arquivo [\"']?([^\"']+)[\"']?(?: (?:ao|com o|no)(?: agente)? [\"']?([^\"']+)[\"']?)?"
            ]
        }
        
        # Compila todas as expressões regulares para melhor desempenho
        self.compiled_patterns = {}
        for command, patterns in self.command_patterns.items():
            self.compiled_patterns[command] = [re.compile(p, re.IGNORECASE) for p in patterns]
        
        # Se não recebeu um session_id, tenta carregar da configuração
        if not session_id:
            config_file = os.path.expanduser("~/.arcee/config.json")
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        config = json.load(f)
                        session_id = config.get("mcp_session_id")
                        logger.info(f"Carregada sessão MCP: {session_id}")
                except Exception as e:
                    logger.error(f"Erro ao carregar configuração MCP: {e}")
                    session_id = None
        
        # Inicializa o gerenciador de tarefas
        try:
            self.task_manager = TaskManagerFactory.create("tess", session_id=session_id)
            if not self.task_manager:
                raise ValueError("Gerenciador TESS não disponível")
                
            # Verifica se o gerenciador é do tipo correto - importação direta
            if not isinstance(self.task_manager, TessTaskManager):
                logger.error("O gerenciador retornado não é do tipo TessTaskManager")
                raise ValueError("Tipo de gerenciador inválido")
                
            logger.info("Gerenciador TESS inicializado com sucesso")
        except Exception as e:
            logger.error(f"Não foi possível inicializar o gerenciador TESS: {str(e)}")
            raise ValueError(f"Gerenciador de tarefas TESS não disponível: {str(e)}")
    
    def detect_command(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Detecta um comando em linguagem natural a partir do texto fornecido.
        
        Args:
            text: Texto contendo o comando em linguagem natural.
            
        Returns:
            Dicionário contendo o comando e parâmetros, ou comando "conversa" para mensagens informais.
        """
        text = text.lower().strip()
        
        # Verificar saudações comuns primeiro
        saudacoes = ["oi", "olá", "ola", "hello", "hi", "tudo bem", "como vai"]
        if text in saudacoes or any(s == text for s in saudacoes):
            return {
                "command": "saudacao",
                "message": text
            }
        
        # Verifica cada tipo de comando
        for command, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                match = pattern.search(text)
                if match:
                    # Extrai os parâmetros do comando
                    params = match.groups()
                    
                    # Monta o dicionário de retorno com base no tipo de comando
                    result = {"command": command}
                    
                    if command == "listar_agentes":
                        pass  # Não precisa de parâmetros adicionais
                    
                    elif command == "obter_agente":
                        result["name"] = params[0].strip() if params[0] else ""
                    
                    elif command == "executar_agente":
                        result["name"] = params[0].strip() if params[0] else ""
                        result["message"] = params[1].strip() if len(params) > 1 and params[1] else ""
                    
                    elif command == "listar_arquivos":
                        pass  # Não precisa de parâmetros adicionais
                    
                    elif command == "vincular_arquivo":
                        result["file_path"] = params[0].strip() if params[0] else ""
                        result["agent_name"] = params[1].strip() if len(params) > 1 and params[1] else ""
                    
                    return result
        
        # Se não encontrou um comando específico, trata como uma conversa informal
        return {
            "command": "conversa",
            "message": text
        }
    
    def execute_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa o comando detectado.
        
        Args:
            command_data: Dados do comando a ser executado.
            
        Returns:
            Resultado da execução do comando.
        """
        if not self.task_manager:
            return {"success": False, "error": "Gerenciador de tarefas não inicializado"}
        
        command = command_data.get("command")
        
        try:
            # Executa o comando com base no tipo
            if command == "listar_agentes":
                result = self._listar_agentes()
            elif command == "obter_agente":
                result = self._obter_agente(command_data)
            elif command == "executar_agente":
                result = self._executar_agente(command_data)
            elif command == "listar_arquivos":
                result = self._listar_arquivos()
            elif command == "vincular_arquivo":
                result = self._vincular_arquivo(command_data)
            elif command == "saudacao":
                result = self._saudacao(command_data)
            elif command == "conversa":
                result = self._conversar(command_data)
            else:
                result = {"success": False, "error": f"Comando não suportado: {command}"}
            
            return result
                    
        except Exception as e:
            logger.exception(f"Erro ao executar comando: {e}")
            return {"success": False, "error": f"Erro ao executar comando: {str(e)}"}
    
    def _saudacao(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Responde a saudações comuns sem chamar API.
        
        Args:
            command_data: Dados da mensagem.
            
        Returns:
            Resposta amigável.
        """
        mensagem = command_data.get("message", "").lower().strip()
        
        if "tudo bem" in mensagem:
            resposta = "Tudo ótimo, obrigado por perguntar! Como posso ajudar você hoje?"
        elif "bom dia" in mensagem:
            resposta = "Bom dia! Como posso ajudar você hoje?"
        elif "boa tarde" in mensagem:
            resposta = "Boa tarde! Em que posso ser útil?"
        elif "boa noite" in mensagem:
            resposta = "Boa noite! Precisa de alguma ajuda?"
        else:
            resposta = "Olá! Como posso ajudar você hoje? Você pode pedir para 'listar agentes' ou 'executar agente', por exemplo."
        
        return {
            "success": True,
            "message": resposta
        }
    
    def _conversar(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa uma conversa informal com o TESS.
        Para saudações comuns, responde diretamente sem chamar a API.
        
        Args:
            command_data: Dados da mensagem.
            
        Returns:
            Resultado da conversa.
        """
        mensagem = command_data.get("message", "").lower().strip()
        if not mensagem:
            return {
                "success": False,
                "error": "Mensagem vazia. Por favor, tente novamente."
            }
        
        logger.info(f"Processando mensagem de conversa: '{mensagem}'")
        
        # Responde diretamente com orientação sobre comandos disponíveis
        return {
            "success": True,
            "message": (
                "Olá! Sou o assistente TESS e posso ajudar com comandos específicos. "
                "Você pode usar comandos como:\n"
                "- 'listar agentes'\n"
                "- 'executar agente <nome> com mensagem <texto>'\n"
                "- 'listar arquivos'\n"
                "Como posso ajudar você hoje?"
            )
        }
    
    def _listar_agentes(self) -> Dict[str, Any]:
        """
        Lista todos os agentes disponíveis
        
        Returns:
            Dicionário com o resultado da operação
        """
        try:
            # Adiciona log para ajudar a depurar
            logger.info("Iniciando listagem de agentes TESS")
            
            # Obtém a lista de agentes
            agentes = self.task_manager.listar_agentes()
            
            if not agentes:
                return {"success": True, "message": "Nenhum agente encontrado"}
                
            # Cria a mensagem formatada
            message = "Agentes disponíveis:\n"
            for idx, agent in enumerate(agentes, 1):
                message += f"{idx}. {agent.get('title', 'Sem título')} (ID: {agent.get('id', 'N/A')})\n"
                
            return {"success": True, "message": message, "data": agentes}
            
        except Exception as e:
            logger.exception(f"Erro ao listar agentes: {e}")
            return {"success": False, "error": f"Erro ao listar agentes: {str(e)}"}
    
    def _obter_agente(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtém detalhes de um agente específico
        
        Args:
            command_data: Dados do comando
            
        Returns:
            Dicionário com o resultado da operação
        """
        try:
            agent_name = command_data.get("name", "")
            if not agent_name:
                return {"success": False, "error": "Nome do agente não fornecido"}
                
            # Procura o agente pelo nome ou ID
            agent = self._encontrar_agente(agent_name)
            if not agent:
                return {"success": False, "error": f"Agente '{agent_name}' não encontrado"}
                
            # Obtém os detalhes completos do agente
            agent_id = agent.get("id")
            agent_details = self.task_manager.obter_agente(agent_id)
            
            if not agent_details:
                return {"success": False, "error": f"Não foi possível obter detalhes do agente {agent_id}"}
                
            # Cria a mensagem formatada
            message = f"Detalhes do Agente: {agent_details.get('title', 'Sem título')}\n"
            message += f"ID: {agent_details.get('id', 'N/A')}\n"
            message += f"Descrição: {agent_details.get('description', 'Sem descrição')}\n"
            message += f"Criado em: {agent_details.get('created_at', 'N/A')}\n"
            message += f"Atualizado em: {agent_details.get('updated_at', 'N/A')}\n"
                
            return {"success": True, "message": message, "data": agent_details}
            
        except Exception as e:
            logger.exception(f"Erro ao obter agente: {e}")
            return {"success": False, "error": f"Erro ao obter agente: {str(e)}"}

    def _executar_agente(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa um agente com uma mensagem
        
        Args:
            command_data: Dados do comando
            
        Returns:
            Dicionário com o resultado da operação
        """
        try:
            agent_name = command_data.get("name", "")
            message = command_data.get("message", "")
            
            if not agent_name:
                return {"success": False, "error": "Nome do agente não fornecido"}
                
            if not message:
                return {"success": False, "error": "Mensagem não fornecida"}
                
            # Procura o agente pelo nome ou ID
            agent = self._encontrar_agente(agent_name)
            if not agent:
                return {"success": False, "error": f"Agente '{agent_name}' não encontrado"}
                
            # Obtém o ID do agente
            agent_id = agent.get("id")
            
            # Preparar os parâmetros para o agente no formato correto
            parametros = {
                "temperature": "0.5",
                "model": "tess-ai-light",
                "maxlength": 500,
                "language": "Portuguese (Brazil)"
            }
            
            # Determinar qual campo usar para a mensagem com base no tipo do agente
            agent_title = agent.get("title", "").lower()
            if "e-mail-de-venda" in agent_title or "email-de-venda" in agent_title:
                parametros.update({
                    "nome-do-produto": "TESS AI",
                    "url-do-produto": "https://tess.pareto.io",
                    "diferenciais-do-produto": message
                })
            elif "linkedin" in agent_title or "post" in agent_title:
                parametros.update({
                    "texto": message
                })
            else:
                # Caso genérico, usa a mensagem como conteúdo
                parametros.update({
                    "mensagem": message
                })
            
            # Executa o agente com os parâmetros corretos
            result = self.task_manager.executar_agente(agent_id, parametros)
            
            # Se tudo correu bem, extrai a resposta
            if result.get("success"):
                return {"success": True, "message": result.get("output", ""), "data": result}
            else:
                # Houve um erro
                return {"success": False, "error": result.get("error", "Erro ao executar agente")}
            
        except Exception as e:
            logger.exception(f"Erro ao executar agente: {e}")
            return {"success": False, "error": f"Erro ao executar agente: {str(e)}"}

    def _listar_arquivos(self) -> Dict[str, Any]:
        """
        Lista todos os arquivos disponíveis
        
        Returns:
            Dicionário com o resultado da operação
        """
        try:
            # Obtém a lista de arquivos
            arquivos = self.task_manager.listar_arquivos()
            
            if not arquivos:
                return {"success": True, "message": "Nenhum arquivo encontrado"}
                
            # Cria a mensagem formatada
            message = "Arquivos disponíveis:\n"
            for idx, arquivo in enumerate(arquivos, 1):
                message += f"{idx}. {arquivo.get('filename', 'Sem nome')} (ID: {arquivo.get('id', 'N/A')})\n"
                
            return {"success": True, "message": message, "data": arquivos}
            
        except Exception as e:
            logger.exception(f"Erro ao listar arquivos: {e}")
            return {"success": False, "error": f"Erro ao listar arquivos: {str(e)}"}

    def _vincular_arquivo(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Faz upload de um arquivo
        
        Args:
            command_data: Dados do comando
            
        Returns:
            Dicionário com o resultado da operação
        """
        try:
            file_path = command_data.get("file_path", "")
            if not file_path:
                return {"success": False, "error": "Caminho do arquivo não fornecido"}
                
            # Verifica se o arquivo existe
            if not os.path.exists(file_path):
                return {"success": False, "error": f"Arquivo não encontrado: {file_path}"}
                
            # Faz upload do arquivo
            result = self.task_manager.vincular_arquivo(file_path)
            
            if not result:
                return {"success": False, "error": "Erro ao processar o upload do arquivo"}
                
            # Cria a mensagem formatada
            message = "Upload concluído com sucesso!\n"
            message += f"ID: {result.get('id', 'N/A')}\n"
            message += f"Nome: {result.get('filename', 'Sem nome')}\n"
                
            return {"success": True, "message": message, "data": result}
            
        except Exception as e:
            logger.exception(f"Erro ao fazer upload de arquivo: {e}")
            return {"success": False, "error": f"Erro ao fazer upload de arquivo: {str(e)}"}
            
    def _encontrar_agente(self, nome_ou_id: str) -> Optional[Dict[str, Any]]:
        """
        Encontra um agente pelo nome ou ID na lista de agentes
        
        Args:
            nome_ou_id: Nome ou ID do agente
            
        Returns:
            Dicionário com os dados do agente, ou None se não encontrado
        """
        # Obtém a lista de agentes
        agentes = self.task_manager.listar_agentes()
        
        # Se o nome_ou_id é um ID numérico, procura por correspondência exata de ID
        try:
            id_numerico = int(nome_ou_id)
            for agente in agentes:
                if agente.get("id") == id_numerico:
                    return agente
        except ValueError:
            # Não é um ID numérico, continua com a busca por nome
            pass
            
        # Procura por correspondência exata ou parcial no título
        nome_ou_id_lower = nome_ou_id.lower()
        for agente in agentes:
            # Verifica correspondência exata
            if agente.get("title", "").lower() == nome_ou_id_lower:
                return agente
                
        # Procura por correspondência parcial no título
        for agente in agentes:
            if nome_ou_id_lower in agente.get("title", "").lower():
                return agente
        
        # Não encontrou nenhum agente
        return None 