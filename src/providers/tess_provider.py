"""
Provedor para interação com a API do TESS.
"""

import os
import requests
import json
import logging
from typing import Dict, List, Any, Tuple, Optional
from ..utils.logging import get_logger

# Configuração de logger
logger = get_logger(__name__)

class TessProvider:
    """Classe para interagir com a API do TESS."""
    
    def __init__(self):
        """Inicializa o provedor TESS com a API key do ambiente."""
        self.api_key = os.getenv("TESS_API_KEY")
        self.api_url = os.getenv("TESS_API_URL", "https://tess.pareto.io/api")
        self.local_server_url = os.getenv("TESS_LOCAL_SERVER_URL", "http://localhost:3000")
        self.use_local_server = os.getenv("USE_LOCAL_TESS", "True").lower() in ("true", "1", "t")
        
        if not self.api_key and not self.use_local_server:
            logger.error("TESS_API_KEY não configurada no ambiente")
            raise ValueError("TESS_API_KEY não configurada. Configure no arquivo .env")
            
        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        logger.debug(f"TessProvider inicializado (servidor local: {self.use_local_server})")
        
    def health_check(self) -> Tuple[bool, str]:
        """Verifica se a API do TESS está disponível."""
        if self.use_local_server:
            try:
                response = requests.get(
                    f"{self.local_server_url}/health",
                    timeout=10
                )
                response.raise_for_status()
                return True, "Conexão com servidor local estabelecida"
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro ao conectar com o servidor TESS local: {str(e)}")
                return False, f"Servidor local indisponível: {str(e)}"
        else:
            try:
                response = requests.get(
                    f"{self.api_url}/agents",
                    headers=self.headers,
                    params={"per_page": 1},
                    timeout=10
                )
                response.raise_for_status()
                return True, "Conexão estabelecida"
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro ao conectar com a API TESS: {str(e)}")
                return False, str(e)
    
    def list_agents(self, page: int = 1, per_page: int = 15) -> List[Dict[str, Any]]:
        """Lista os agentes disponíveis na API."""
        if self.use_local_server:
            # Servidor local não tem função de listagem, retornamos um agente simulado
            logger.debug("Usando servidor local - retornando agente simulado")
            return [{
                "id": "local-tess",
                "name": "Assistente TESS Local",
                "description": "Assistente local para conversa e consultas"
            }]
        
        try:
            response = requests.get(
                f"{self.api_url}/agents",
                headers=self.headers,
                params={"page": page, "per_page": per_page},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao listar agentes: {str(e)}")
            return []
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Obtém detalhes de um agente específico."""
        if self.use_local_server:
            # Servidor local não tem função de detalhes, retornamos um agente simulado
            logger.debug("Usando servidor local - retornando detalhes simulados")
            return {
                "id": "local-tess",
                "name": "Assistente TESS Local",
                "description": "Assistente local para conversa e consultas",
                "questions": []
            }
        
        try:
            response = requests.get(
                f"{self.api_url}/agents/{agent_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter agente {agent_id}: {str(e)}")
            return None
    
    def execute_agent(self, agent_id: str, params: Dict[str, Any], 
                      messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Executa um agente com os parâmetros e mensagens fornecidos."""
        
        if self.use_local_server:
            try:
                # Obter a última mensagem do usuário
                last_user_message = None
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        last_user_message = msg.get("content", "")
                        break
                
                if not last_user_message:
                    return {"content": "Por favor, forneça uma mensagem."}
                
                # Verificar se temos o MCP disponível
                try:
                    from ..tools.mcpx_simple import MCPRunClient
                    from ..providers.mcp_provider import MCPProvider
                    
                    # Obter o ID de sessão do MCP
                    session_id = MCPProvider.get_mcp_session_id()
                    
                    if session_id:
                        # Tentar usar o chat_completion do MCP diretamente
                        client = MCPRunClient(session_id=session_id)
                        
                        # Preparar mensagens no formato adequado para o chat_completion
                        # Limitamos a 10 mensagens para evitar problemas
                        mcp_messages = messages[-10:]
                        
                        # Executar o chat_completion com o MCP.run
                        logger.debug("Tentando usar chat_completion do MCP...")
                        
                        result = client.run_tool("chat_completion", {
                            "messages": mcp_messages,
                            "model": params.get("model", "gpt-3.5-turbo"),
                            "temperature": float(params.get("temperature", 0.7)),
                            "max_tokens": int(params.get("maxlength", 500))
                        })
                        
                        # Verificar se temos uma resposta
                        if result and not "error" in result:
                            # Extrair o texto da resposta
                            if "text" in result:
                                return {"content": result["text"], "status": "completed"}
                            elif "content" in result:
                                return {"content": result["content"], "status": "completed"}
                        else:
                            logger.warning(f"Erro ao usar chat_completion do MCP: {result.get('error', 'Desconhecido')}")
                    else:
                        logger.warning("Sessão MCP não encontrada, tentando TESS local")
                except ImportError:
                    logger.warning("Módulo MCPRunClient não disponível, tentando TESS local")
                except Exception as e:
                    logger.warning(f"Erro ao usar chat_completion do MCP: {str(e)}")
                
                # Se chegou até aqui, tenta o endpoint /chat
                # Preparar a requisição para o servidor local
                data = {
                    "messages": messages,
                    "model": params.get("model", "gpt-3.5-turbo"),
                    "temperature": float(params.get("temperature", 0.7)),
                    "max_tokens": int(params.get("maxlength", 500))
                }
                
                # Fazer a requisição para o servidor local
                logger.debug(f"Enviando requisição para o servidor local")
                response = requests.post(
                    f"{self.local_server_url}/chat",
                    json=data,
                    timeout=60
                )
                
                # Se tiver erro 404, use o endpoint /health como fallback para simular resposta
                if response.status_code == 404:
                    # Tentar usar o health_check como ferramenta do MCP
                    try:
                        from ..tools.mcpx_simple import MCPRunClient
                        from ..providers.mcp_provider import MCPProvider
                        
                        # Obter o ID de sessão do MCP
                        session_id = MCPProvider.get_mcp_session_id()
                        
                        if session_id:
                            # Criar cliente MCP
                            client = MCPRunClient(session_id=session_id)
                            
                            # Verificar se a ferramenta health_check existe
                            tools = client.get_tools()
                            tool_names = [tool.get('name') for tool in tools]
                            
                            if "health_check" in tool_names:
                                # Usar health_check para verificar a mensagem
                                health_result = client.run_tool("health_check", {
                                    "message": last_user_message
                                })
                                
                                if health_result and not "error" in health_result:
                                    return {
                                        "content": f"✅ Sua mensagem foi recebida: '{last_user_message}'\n\n" +
                                                  f"Resposta do servidor: {health_result.get('status', 'OK')}\n" +
                                                  f"Posso usar as seguintes ferramentas MCP:\n" +
                                                  "\n".join([f"- {name}" for name in tool_names]),
                                        "status": "completed"
                                    }
                    except Exception as e:
                        logger.warning(f"Erro ao usar health_check do MCP: {str(e)}")
                            
                    logger.warning("Endpoint /chat não encontrado, usando fallback")
                    # Simular uma resposta baseada em uma função de resposta básica
                    resposta = self._gerar_resposta_fallback(last_user_message, messages)
                    return {
                        "content": resposta,
                        "status": "completed"
                    }
                
                response.raise_for_status()
                result = response.json()
                
                # Formatar a resposta de acordo com o protocolo esperado
                return {
                    "content": result.get("text", result.get("content", "Resposta do servidor local")),
                    "status": "completed"
                }
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro ao comunicar com servidor local: {str(e)}")
                return {
                    "content": f"Erro de comunicação com o servidor local: {str(e)}. " +
                               "Verifique se o servidor está rodando com 'arcee_cli/scripts/start_tess_server_background.sh'."
                }
        
        try:
            # Preparar corpo da requisição
            data = {
                **params,
                "waitExecution": True
            }
            
            # Se houver mensagens, incluir na última mensagem do usuário
            if messages:
                last_user_message = None
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        last_user_message = msg.get("content", "")
                        break
                
                if last_user_message:
                    # Adicionar a mensagem ao campo apropriado
                    # Normalmente seria "texto" para o agente de post LinkedIn
                    data["texto"] = last_user_message
            
            logger.debug(f"Executando agente {agent_id} com params: {json.dumps(data)}")
            
            # Fazer requisição para a API
            response = requests.post(
                f"{self.api_url}/agents/{agent_id}/execute",
                headers=self.headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            # Verificar resultado
            if "responses" in result and len(result["responses"]) > 0:
                response_data = result["responses"][0]
                
                if response_data.get("status") == "succeeded" and response_data.get("output"):
                    # Construir resposta no formato esperado pelo chat
                    return {
                        "content": response_data["output"],
                        "id": response_data.get("id", ""),
                        "status": "completed"
                    }
            
            # Se não conseguimos extrair a resposta formatada, retornar o resultado bruto
            return {"content": "Não foi possível obter resposta do agente.", "raw": result}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao executar agente {agent_id}: {str(e)}")
            raise RuntimeError(f"Erro ao processar solicitação: {str(e)}")
            
    def _gerar_resposta_fallback(self, mensagem: str, historico: List[Dict[str, str]]) -> str:
        """
        Gera uma resposta de fallback quando o endpoint de chat não está disponível.
        
        Args:
            mensagem: Última mensagem do usuário
            historico: Histórico completo da conversa
            
        Returns:
            Resposta gerada
        """
        try:
            # Tentar usar ferramentas MCP
            from ..tools.mcpx_simple import MCPRunClient
            from ..providers.mcp_provider import MCPProvider
            
            # Obter o ID de sessão do MCP
            session_id = MCPProvider.get_mcp_session_id()
            
            if session_id:
                # Tentar usar search_info do MCP
                client = MCPRunClient(session_id=session_id)
                
                # Verificar se a ferramenta search_info existe
                tools = client.get_tools()
                tool_names = [tool.get('name') for tool in tools]
                
                if "search_info" in tool_names:
                    # Usar search_info para buscar informações relevantes
                    search_result = client.run_tool("search_info", {
                        "query": mensagem
                    })
                    
                    if search_result and not "error" in search_result:
                        info = search_result.get("information", "Não foi possível encontrar informações relevantes.")
                        return f"Aqui está o que encontrei sobre sua pergunta:\n\n{info}\n\nPosso ajudar com mais alguma coisa?"
        except Exception as e:
            logger.warning(f"Erro ao usar search_info do MCP: {str(e)}")
        
        # Mensagem de fallback padrão
        comandos_disponiveis = [
            "listar ferramentas mcp - Mostra as ferramentas disponíveis",
            "configurar mcp - Configura o MCP com uma sessão específica",
            "executar ferramenta <nome> - Executa uma ferramenta MCP específica"
        ]
        
        resposta = (
            f"Olá! Recebi sua mensagem: '{mensagem}'\n\n"
            f"O servidor de chat está online, mas o endpoint de processamento ainda não está completamente implementado.\n\n"
            f"No entanto, você pode usar os seguintes comandos MCP:\n"
        )
        
        for cmd in comandos_disponiveis:
            resposta += f"- {cmd}\n"
            
        resposta += "\nExperimente usar um desses comandos para interagir com o MCP!"
        
        return resposta 