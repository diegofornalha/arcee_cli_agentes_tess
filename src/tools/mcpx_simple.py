#!/usr/bin/env python
"""
Cliente simplificado para interação com o MCP.run através do proxy TESS.
"""

import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

logger = logging.getLogger(__name__)

class MCPRunClient:
    """Cliente simplificado para o MCP.run usando proxy TESS."""
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Inicializa o cliente MCP.
        
        Args:
            session_id: ID de sessão do MCP.run (opcional)
        """
        self.session_id = session_id or os.getenv("MCP_SESSION_ID")
        self.mcp_sse_url = os.getenv("MCP_SSE_URL")
        
        # Configurar URLs do TESS
        self.tess_api_key = os.getenv("TESS_API_KEY")
        self.use_local = os.getenv("USE_LOCAL_TESS", "False").lower() == "true"
        
        if self.use_local:
            base_url = os.getenv("TESS_LOCAL_SERVER_URL", "http://localhost:3000")
        else:
            base_url = os.getenv("TESS_API_URL", "https://tess.pareto.io")
            
        self.api_url = f"{base_url}/api"
        logger.info(f"Usando servidor TESS: {self.api_url}")
        
        if not self.session_id:
            raise ValueError("ID de sessão MCP não fornecido")
            
        if not self.tess_api_key:
            raise ValueError("TESS_API_KEY não configurada")
            
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Faz uma requisição para o proxy TESS.
        
        Args:
            method: Método HTTP (GET, POST, etc)
            endpoint: Endpoint da API
            **kwargs: Argumentos adicionais para requests
            
        Returns:
            Resposta da API
        """
        # Adicionar headers de autenticação
        headers = kwargs.pop("headers", {})
        headers.update({
            "Authorization": f"Bearer {self.tess_api_key}",
            "Content-Type": "application/json"
        })
        
        # Adicionar informações do MCP nos parâmetros
        params = kwargs.pop("params", {})
        params.update({
            "session_id": self.session_id,
            "mcp_sse_url": self.mcp_sse_url
        })
        
        # Fazer requisição
        url = f"{self.api_url}/{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            **kwargs
        )
        
        # Log para debug
        logger.debug(f"Request URL: {url}")
        logger.debug(f"Request headers: {headers}")
        logger.debug(f"Request params: {params}")
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response body: {response.text}")
        
        # Verificar resposta
        response.raise_for_status()
        return response.json()
            
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de ferramentas disponíveis através do proxy TESS.
        
        Returns:
            Lista de ferramentas
        """
        try:
            response = self._make_request(
                method="GET",
                endpoint="mcp/tools"
            )
            
            # Processar resposta
            tools = response.get("tools", [])
            logger.info(f"Obtidas {len(tools)} ferramentas via proxy TESS")
            return tools
            
        except Exception as e:
            logger.error(f"Erro ao obter ferramentas via proxy TESS: {e}")
            raise
            
    def run_tool(self, tool_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executa uma ferramenta específica através do proxy TESS.
        
        Args:
            tool_name: Nome da ferramenta
            params: Parâmetros para a ferramenta (opcional)
            
        Returns:
            Resultado da execução
        """
        try:
            # Preparar dados
            data = {
                "tool": tool_name,
                "params": params or {}
            }
            
            # Executar via proxy TESS
            response = self._make_request(
                method="POST",
                endpoint="mcp/execute",
                json=data
            )
            
            logger.info(f"Ferramenta {tool_name} executada via proxy TESS")
            return response
            
        except Exception as e:
            logger.error(f"Erro ao executar ferramenta {tool_name} via proxy TESS: {e}")
            raise

def configure_mcprun(session_id: Optional[str] = None) -> Optional[str]:
    """
    Configura o cliente MCP.run.
    
    Args:
        session_id: ID de sessão existente (opcional)
        
    Returns:
        ID de sessão configurado ou None se falhou
    """
    try:
        # Se não foi fornecido, tentar obter do ambiente
        session_id = session_id or os.getenv("MCP_SESSION_ID")
        
        if not session_id:
            logger.error("ID de sessão MCP não fornecido")
            return None
            
        # Criar cliente para testar configuração
        client = MCPRunClient(session_id=session_id)
        
        # Testar obtendo ferramentas
        tools = client.get_tools()
        logger.info(f"Encontradas {len(tools)} ferramentas disponíveis via proxy TESS")
        
        return session_id
        
    except Exception as e:
        logger.error(f"Erro ao configurar MCP: {e}")
        return None 