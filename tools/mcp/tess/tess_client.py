#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cliente para API da TESS AI via MCP.
"""

import os
import json
import subprocess
from typing import Dict, List, Any, Optional, Union, cast

class TessClient:
    """Cliente para interagir com a API da TESS AI via MCP"""
    
    def __init__(self, api_key: Optional[str] = None, mcp_session: Optional[str] = None):
        """
        Inicializa o cliente TESS
        
        Args:
            api_key: API Key da TESS (opcional, padrão: variável de ambiente TESS_API_KEY)
            mcp_session: ID da sessão MCP (opcional, padrão: variável de ambiente MCP_SESSION_ID)
        """
        self.api_key = api_key or os.getenv("TESS_API_KEY") or ""
        self.mcp_session = mcp_session or os.getenv("MCP_SESSION_ID") or ""
        
        if not self.api_key:
            raise ValueError("API Key da TESS não encontrada. Defina a variável de ambiente TESS_API_KEY ou forneça a chave no construtor.")
            
        if not self.mcp_session:
            raise ValueError("Sessão MCP não encontrada. Defina a variável de ambiente MCP_SESSION_ID ou forneça a sessão no construtor.")
    
    def execute_mcp_command(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """
        Executa um comando MCP
        
        Args:
            tool_name: Nome da ferramenta TESS a executar
            params: Parâmetros para a ferramenta
            
        Returns:
            Resultado da execução (pode ser lista ou dicionário)
        """
        # Converte os parâmetros para JSON
        params_json = json.dumps(params)
        
        # Comando MCP
        cmd = [
            "mcpx", "run", f"mcp-server-agno.{tool_name}",
            "--json", params_json,
            "--session", self.mcp_session
        ]
        
        try:
            # Executa o comando
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Analisa a saída como JSON
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"error": "Falha ao analisar resposta JSON", "raw": result.stdout}
                
        except subprocess.CalledProcessError as e:
            return {"error": f"Falha ao executar comando MCP: {e}", "stderr": e.stderr}
    
    # === Métodos para Agentes ===
    
    def listar_agentes(self, page: int = 1, per_page: int = 15) -> Dict[str, Any]:
        """
        Lista todos os agentes disponíveis
        
        Args:
            page: Número da página (padrão: 1)
            per_page: Itens por página (padrão: 15)
            
        Returns:
            Lista de agentes
        """
        return cast(Dict[str, Any], self.execute_mcp_command("listar_agentes_tess", {
            "page": page,
            "per_page": per_page
        }))
    
    def obter_agente(self, agent_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes de um agente específico
        
        Args:
            agent_id: ID do agente
            
        Returns:
            Detalhes do agente
        """
        return cast(Dict[str, Any], self.execute_mcp_command("obter_agente_tess", {
            "agent_id": agent_id
        }))
    
    def executar_agente(self, agent_id: str, messages: List[Dict[str, str]], 
                      temperature: str = "0.5", model: str = "agno-ai-light",
                      tools: str = "no-tools", file_ids: List[int] = [], 
                      wait_execution: bool = False) -> Dict[str, Any]:
        """
        Executa um agente
        
        Args:
            agent_id: ID do agente a ser executado
            messages: Lista de mensagens no formato [{role: "user", content: "mensagem"}]
            temperature: Temperatura para geração (0-1, padrão: 0.5)
            model: Modelo a ser usado (padrão: agno-ai-light)
            tools: Ferramentas a serem habilitadas (padrão: no-tools)
            file_ids: IDs dos arquivos a serem anexados
            wait_execution: Se deve esperar pela execução completa (padrão: False)
            
        Returns:
            Resultado da execução do agente
        """
        return cast(Dict[str, Any], self.execute_mcp_command("executar_agente_tess", {
            "agent_id": agent_id,
            "messages": messages,
            "temperature": temperature,
            "model": model,
            "tools": tools,
            "file_ids": file_ids,
            "waitExecution": wait_execution
        }))
    
    # === Métodos para Arquivos ===
    
    def listar_arquivos(self, page: int = 1, per_page: int = 15) -> Dict[str, Any]:
        """
        Lista todos os arquivos disponíveis
        
        Args:
            page: Número da página (padrão: 1)
            per_page: Itens por página (padrão: 15)
            
        Returns:
            Lista de arquivos
        """
        return cast(Dict[str, Any], self.execute_mcp_command("listar_arquivos_tess", {
            "page": page,
            "per_page": per_page
        }))
    
    def obter_arquivo(self, file_id: int) -> Dict[str, Any]:
        """
        Obtém detalhes de um arquivo específico
        
        Args:
            file_id: ID do arquivo
            
        Returns:
            Detalhes do arquivo
        """
        return cast(Dict[str, Any], self.execute_mcp_command("obter_arquivo_tess", {
            "file_id": file_id
        }))
    
    def processar_arquivo(self, file_id: int, options: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Processa um arquivo
        
        Args:
            file_id: ID do arquivo a ser processado
            options: Opções de processamento
            
        Returns:
            Resultado do processamento
        """
        return cast(Dict[str, Any], self.execute_mcp_command("processar_arquivo_tess", {
            "file_id": file_id,
            "options": options
        }))
    
    def upload_arquivo(self, file_path: str, process: bool = False) -> Dict[str, Any]:
        """
        Faz upload de um arquivo
        
        Args:
            file_path: Caminho do arquivo a ser enviado
            process: Processar o arquivo após o upload (padrão: False)
            
        Returns:
            Dados do arquivo enviado
        """
        return cast(Dict[str, Any], self.execute_mcp_command("upload_arquivo_tess", {
            "file_path": file_path,
            "process": process
        }))
    
    def excluir_arquivo(self, file_id: int) -> Dict[str, Any]:
        """
        Exclui um arquivo
        
        Args:
            file_id: ID do arquivo a ser excluído
            
        Returns:
            Resultado da exclusão
        """
        return cast(Dict[str, Any], self.execute_mcp_command("excluir_arquivo_tess", {
            "file_id": file_id
        }))
    
    # === Métodos para Arquivos de Agente ===
    
    def listar_arquivos_agente(self, agent_id: str, page: int = 1, 
                             per_page: int = 15) -> Dict[str, Any]:
        """
        Lista arquivos vinculados a um agente
        
        Args:
            agent_id: ID do agente
            page: Número da página (padrão: 1)
            per_page: Itens por página (padrão: 15)
            
        Returns:
            Lista de arquivos do agente
        """
        return cast(Dict[str, Any], self.execute_mcp_command("listar_arquivos_agente_tess", {
            "agent_id": agent_id,
            "page": page,
            "per_page": per_page
        }))
    
    def vincular_arquivo_agente(self, agent_id: str, file_id: int) -> Dict[str, Any]:
        """
        Vincula um arquivo a um agente
        
        Args:
            agent_id: ID do agente
            file_id: ID do arquivo
            
        Returns:
            Resultado da vinculação
        """
        return cast(Dict[str, Any], self.execute_mcp_command("vincular_arquivo_agente_tess", {
            "agent_id": agent_id,
            "file_id": file_id
        }))
    
    def remover_arquivo_agente(self, agent_id: str, file_id: int) -> Dict[str, Any]:
        """
        Remove um arquivo de um agente
        
        Args:
            agent_id: ID do agente
            file_id: ID do arquivo
            
        Returns:
            Resultado da remoção
        """
        return cast(Dict[str, Any], self.execute_mcp_command("remover_arquivo_agente_tess", {
            "agent_id": agent_id,
            "file_id": file_id
        })) 