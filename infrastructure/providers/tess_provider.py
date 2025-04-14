import os
import requests
import json
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class TessProvider:
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("TESS_API_KEY")
        self.api_url = api_url or os.getenv("TESS_API_URL", "https://agno.pareto.io/api")
        
        if not self.api_key:
            raise ValueError("TESS_API_KEY não configurada")
        
        if not self.api_url:
            raise ValueError("TESS_API_URL não configurada")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def health_check(self) -> Tuple[bool, str]:
        """Verifica a conexão com a API TESS tentando listar agentes"""
        try:
            response = requests.get(
                f"{self.api_url}/agents",
                params={"page": 1, "per_page": 1},
                headers=self.headers
            )
            
            if response.status_code == 401:
                return False, "Erro de autenticação: verifique sua TESS_API_KEY"
            
            response.raise_for_status()
            return True, "Conexão com TESS API estabelecida com sucesso"
            
        except requests.exceptions.ConnectionError:
            return False, "Erro de conexão: não foi possível conectar ao servidor TESS"
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao verificar conexão com TESS API: {str(e)}")
            return False, f"Erro ao conectar com TESS API: {str(e)}"

    def list_agents(self, page: int = 1, per_page: int = 15) -> List[Dict]:
        """Lista os agentes disponíveis"""
        try:
            response = requests.get(
                f"{self.api_url}/agents",
                params={"page": page, "per_page": per_page},
                headers=self.headers
            )
            response.raise_for_status()
            
            # Transformar a resposta em uma lista de dicionários com id e title
            data = response.json()
            agents = []
            for agent in data.get('data', []):
                agents.append({
                    'id': agent.get('id'),
                    'name': agent.get('title'),
                    'description': agent.get('description', '')
                })
            return agents
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao listar agentes: {str(e)}")
            return []

    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Obtém detalhes de um agente específico"""
        try:
            response = requests.get(
                f"{self.api_url}/agents/{agent_id}",
                headers=self.headers
            )
            response.raise_for_status()
            
            agent = response.json()
            return {
                'id': agent.get('id'),
                'name': agent.get('title'),
                'description': agent.get('description', ''),
                'type': agent.get('type', ''),
                'visibility': agent.get('visibility', ''),
                'questions': agent.get('questions', [])
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter agente {agent_id}: {str(e)}")
            return None
            
    def execute_agent(self, agent_id: str, params: Dict[str, Any], messages: List[Dict[str, str]]) -> Dict:
        """Executa um agente com os parâmetros fornecidos e mensagens

        Args:
            agent_id: ID do agente a ser executado
            params: Dicionário com os parâmetros do agente
            messages: Lista de mensagens no formato [{role: "user", content: "mensagem"}]

        Returns:
            Dict: Resposta da execução do agente
        """
        try:
            # Para a API TESS, precisamos extrair a última mensagem do usuário
            # e usá-la como entrada para o agente
            last_user_message = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_user_message = msg.get("content", "")
                    break
                    
            if not last_user_message:
                raise ValueError("Nenhuma mensagem do usuário encontrada no histórico")
            
            # Verificar se estamos no modo auto
            using_auto_mode = params.get("model") == "auto"
            if using_auto_mode:
                logger.info("Usando modo AUTO para seleção dinâmica de modelo")
            
            # Preparar dados para a requisição
            # Na API TESS, enviamos o conteúdo do prompt diretamente
            payload = {
                **params,  # Parâmetros do agente (nome-empresa, etc)
                "prompt": last_user_message  # A última mensagem do usuário é o prompt
            }
            
            # Adicionar parâmetros específicos para o modo auto
            if using_auto_mode:
                payload["return_model_info"] = True
            
            logger.debug(f"Executando agente {agent_id} com payload: {json.dumps(payload)}")
            
            # Executar o agente
            # O endpoint correto é /agents/{id}/execute 
            response = requests.post(
                f"{self.api_url}/agents/{agent_id}/execute",
                headers=self.headers,
                json=payload,
                timeout=60  # Aumentando o timeout para evitar erros por demora na resposta
            )
            
            if response.status_code == 401:
                raise ValueError("Erro de autenticação: verifique sua TESS_API_KEY")
            
            if response.status_code == 404:
                raise ValueError(f"Agente com ID {agent_id} não encontrado")
                
            response.raise_for_status()
            
            response_data = response.json()
            logger.debug(f"Resposta do agente: {json.dumps(response_data)}")
            
            # Extrair informações sobre o modelo usado (quando no modo auto)
            model_used = response_data.get("model_used", None) or params.get("model", "desconhecido")
            
            if using_auto_mode and model_used:
                logger.info(f"Modo AUTO selecionou o modelo: {model_used}")
            
            # Retornar o formato compatível com o esperado pelo chat
            # Na API TESS, a resposta está no campo 'response'
            return {
                'content': response_data.get('response', 'Sem resposta do assistente'),
                'role': 'assistant',
                'agent_id': agent_id,
                'model': model_used
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao executar agente {agent_id}: {str(e)}")
            # Tentar novamente com timeout maior apenas para erros de timeout
            if "timeout" in str(e).lower():
                try:
                    logger.info(f"Tentando novamente com timeout maior para agente {agent_id}")
                    response = requests.post(
                        f"{self.api_url}/agents/{agent_id}/execute",
                        headers=self.headers,
                        json=payload,
                        timeout=120  # Timeout ainda maior para segunda tentativa
                    )
                    response.raise_for_status()
                    
                    response_data = response.json()
                    model_used = response_data.get("model_used", None) or params.get("model", "desconhecido")
                    
                    return {
                        'content': response_data.get('response', 'Sem resposta do assistente'),
                        'role': 'assistant',
                        'agent_id': agent_id,
                        'model': model_used
                    }
                except Exception as retry_error:
                    logger.error(f"Segunda tentativa falhou para agente {agent_id}: {str(retry_error)}")
            
            raise ValueError(f"Erro ao executar agente: {str(e)}") 