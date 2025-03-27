from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tess-mcp-python")

# Criar aplicação FastAPI
app = FastAPI(title="TESS MCP Server")

# Adicionar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Ferramentas MCP -----

class MCPTools:
    @staticmethod
    async def health_check() -> Dict[str, Any]:
        """Verificação de saúde do servidor"""
        return {
            "status": "ok",
            "message": "TESS proxy server is running (Python/FastAPI)",
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    async def search_info(query: str) -> str:
        """Implementação de busca de informações"""
        logger.info(f"Buscando informações para: {query}")
        # Simula um processamento
        await asyncio.sleep(0.5)
        return f"Resultados para '{query}': Encontrados 5 documentos relevantes em {datetime.now().isoformat()}"
    
    @staticmethod
    async def process_image(url: str) -> Dict[str, Any]:
        """Processamento de imagem"""
        logger.info(f"Processando imagem em: {url}")
        # Simula processamento
        await asyncio.sleep(1)
        return {
            "width": 800,
            "height": 600,
            "format": "jpeg",
            "has_faces": True,
            "description": f"Imagem em {url} processada com sucesso",
            "tags": ["imagem", "processada", "teste"]
        }
    
    @staticmethod
    async def chat_completion(prompt: str, history: Optional[list] = None) -> str:
        """Simulação de chat completion"""
        logger.info(f"Processando chat completion, tamanho do prompt: {len(prompt)}")
        # Simula processamento
        await asyncio.sleep(0.3)
        return f"Resposta para: {prompt[:30]}... (gerada em {datetime.now().isoformat()})"
        
    @staticmethod
    async def list_agents(page: int = 1, per_page: int = 15) -> Dict[str, Any]:
        """Lista os agentes disponíveis no sistema"""
        logger.info(f"Listando agentes disponíveis (página {page}, {per_page} por página)")
        # Simula uma lista de agentes
        all_agents = [
            {
                "id": "agent-001",
                "name": "Assistente Geral",
                "description": "Agente para assistência geral e respostas a perguntas",
                "capabilities": ["chat", "search", "recommendations"]
            },
            {
                "id": "agent-002",
                "name": "Especialista em Código",
                "description": "Agente especializado em programação e desenvolvimento",
                "capabilities": ["code_review", "debugging", "code_generation"]
            },
            {
                "id": "agent-003",
                "name": "Analista de Dados",
                "description": "Agente para análise e visualização de dados",
                "capabilities": ["data_analysis", "chart_generation", "statistics"]
            }
        ]
        
        # Aplicar paginação
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_agents = all_agents[start_idx:end_idx]
        
        return {
            "agents": paginated_agents,
            "total": len(all_agents),
            "page": page,
            "per_page": per_page,
            "total_pages": (len(all_agents) + per_page - 1) // per_page
        }
    
    @staticmethod
    async def get_agent(agent_id: str) -> Dict[str, Any]:
        """Obtém detalhes de um agente específico"""
        logger.info(f"Obtendo detalhes do agente: {agent_id}")
        
        # Simula busca do agente por ID
        agents = {
            "agent-001": {
                "id": "agent-001",
                "name": "Assistente Geral",
                "description": "Agente para assistência geral e respostas a perguntas",
                "capabilities": ["chat", "search", "recommendations"],
                "created_at": "2023-05-15T10:00:00Z",
                "updated_at": "2023-08-22T14:30:00Z",
                "version": "1.2.3",
                "status": "active",
                "metadata": {
                    "training_data": "general_knowledge_2023",
                    "owner": "tess_team",
                    "language": "pt-br"
                }
            },
            "agent-002": {
                "id": "agent-002",
                "name": "Especialista em Código",
                "description": "Agente especializado em programação e desenvolvimento",
                "capabilities": ["code_review", "debugging", "code_generation"],
                "created_at": "2023-06-10T09:15:00Z",
                "updated_at": "2023-09-05T11:45:00Z",
                "version": "2.0.1",
                "status": "active",
                "metadata": {
                    "training_data": "code_repositories_2023",
                    "owner": "dev_team",
                    "language": "multilingual",
                    "supported_languages": ["python", "javascript", "rust", "go"]
                }
            },
            "agent-003": {
                "id": "agent-003",
                "name": "Analista de Dados",
                "description": "Agente para análise e visualização de dados",
                "capabilities": ["data_analysis", "chart_generation", "statistics"],
                "created_at": "2023-07-20T14:20:00Z",
                "updated_at": "2023-10-12T16:00:00Z",
                "version": "1.5.0",
                "status": "active",
                "metadata": {
                    "training_data": "data_science_2023",
                    "owner": "analytics_team",
                    "language": "multilingual",
                    "data_connectors": ["csv", "json", "sql", "excel"]
                }
            }
        }
        
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail=f"Agente com ID '{agent_id}' não encontrado")
        
        return agents[agent_id]
    
    @staticmethod
    async def execute_agent(agent_id: str, model: str = "default", tools: list = None, 
                           messages: list = None, file_ids: list = None, 
                           temperature: float = 0.7, wait_execution: bool = True) -> Dict[str, Any]:
        """Executa um agente com mensagens específicas"""
        logger.info(f"Executando agente: {agent_id}")
        
        if not messages:
            raise HTTPException(status_code=400, detail="Parâmetro 'messages' é obrigatório")
        
        # Verificar se o agente existe
        valid_agent_ids = ["agent-001", "agent-002", "agent-003"]
        if agent_id not in valid_agent_ids:
            raise HTTPException(status_code=404, detail=f"Agente com ID '{agent_id}' não encontrado")
        
        # Simula tempo de processamento baseado no wait_execution
        if wait_execution:
            await asyncio.sleep(2.0)  # Simula tempo de processamento completo
        else:
            await asyncio.sleep(0.2)  # Resposta rápida para modo assíncrono
        
        # Prepara resposta simulada
        agent_names = {
            "agent-001": "Assistente Geral",
            "agent-002": "Especialista em Código",
            "agent-003": "Analista de Dados"
        }
        
        # Determina a última mensagem do usuário
        user_message = "Olá"
        for msg in messages:
            if isinstance(msg, dict) and msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # Gera resposta baseada no tipo de agente
        responses = {
            "agent-001": f"Olá! Sou o Assistente Geral e estou aqui para ajudar com '{user_message[:30]}...'",
            "agent-002": f"Como Especialista em Código, posso ajudar com '{user_message[:30]}...'. Que linguagem você está usando?",
            "agent-003": f"Analisando sua solicitação: '{user_message[:30]}...'. Quais dados você gostaria de processar?"
        }
        
        return {
            "id": f"execution-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "agent_id": agent_id,
            "agent_name": agent_names.get(agent_id, "Desconhecido"),
            "status": "completed" if wait_execution else "processing",
            "input": {
                "model": model,
                "tools": tools or [],
                "message_count": len(messages),
                "temperature": temperature
            },
            "output": {
                "message": responses.get(agent_id, "Processando..."),
                "timestamp": datetime.now().isoformat(),
                "tokens_used": 150 + len(user_message),
                "processing_time_ms": 1850 if wait_execution else 120
            }
        }
    
    @staticmethod
    async def list_agent_files(agent_id: str, page: int = 1, per_page: int = 15) -> Dict[str, Any]:
        """Lista arquivos associados a um agente"""
        logger.info(f"Listando arquivos do agente {agent_id} (página {page}, {per_page} por página)")
        
        # Verificar se o agente existe
        valid_agent_ids = ["agent-001", "agent-002", "agent-003"]
        if agent_id not in valid_agent_ids:
            raise HTTPException(status_code=404, detail=f"Agente com ID '{agent_id}' não encontrado")
        
        # Simula arquivos diferentes para cada agente
        agent_files = {
            "agent-001": [
                {"id": "file-001", "name": "knowledge_base.txt", "size": 25600, "created_at": "2023-06-15T10:30:00Z", "type": "text"},
                {"id": "file-002", "name": "faq_responses.json", "size": 15800, "created_at": "2023-07-22T09:45:00Z", "type": "json"},
                {"id": "file-003", "name": "agent_config.yaml", "size": 4200, "created_at": "2023-05-18T14:20:00Z", "type": "yaml"}
            ],
            "agent-002": [
                {"id": "file-004", "name": "code_examples.py", "size": 18700, "created_at": "2023-06-25T16:40:00Z", "type": "python"},
                {"id": "file-005", "name": "debugging_guide.md", "size": 22300, "created_at": "2023-08-12T11:35:00Z", "type": "markdown"},
                {"id": "file-006", "name": "development_patterns.json", "size": 31500, "created_at": "2023-07-08T13:50:00Z", "type": "json"},
                {"id": "file-007", "name": "error_handling.js", "size": 9800, "created_at": "2023-09-02T10:15:00Z", "type": "javascript"}
            ],
            "agent-003": [
                {"id": "file-008", "name": "data_schema.json", "size": 12400, "created_at": "2023-08-05T15:20:00Z", "type": "json"},
                {"id": "file-009", "name": "visualization_templates.py", "size": 28900, "created_at": "2023-09-18T12:30:00Z", "type": "python"},
                {"id": "file-010", "name": "sample_dataset.csv", "size": 156000, "created_at": "2023-07-30T09:10:00Z", "type": "csv"}
            ]
        }
        
        files = agent_files.get(agent_id, [])
        
        # Aplicar paginação
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_files = files[start_idx:end_idx]
        
        return {
            "files": paginated_files,
            "total": len(files),
            "page": page,
            "per_page": per_page,
            "total_pages": (len(files) + per_page - 1) // per_page,
            "agent_id": agent_id
        }

# ----- Rotas da API -----

@app.get("/health")
async def health():
    """Endpoint de verificação de saúde"""
    result = await MCPTools.health_check()
    return result

@app.get("/api/mcp/tools")
async def list_tools(request: Request):
    """Lista as ferramentas MCP disponíveis"""
    session_id = request.query_params.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id não fornecido")
    
    # Lista de ferramentas disponíveis
    tools = [
        {
            "name": "health_check",
            "description": "Verifica a saúde do servidor",
            "parameters": {}
        },
        {
            "name": "search_info",
            "description": "Busca informações sobre um tópico",
            "parameters": {
                "query": {"type": "string", "description": "Termo de busca"}
            }
        },
        {
            "name": "process_image",
            "description": "Processa uma imagem e retorna informações",
            "parameters": {
                "url": {"type": "string", "description": "URL da imagem a ser processada"}
            }
        },
        {
            "name": "chat_completion",
            "description": "Gera resposta para um prompt",
            "parameters": {
                "prompt": {"type": "string", "description": "Texto do prompt"},
                "history": {"type": "array", "description": "Histórico de conversa (opcional)"}
            }
        },
        {
            "name": "list_agents",
            "description": "Lista os agentes disponíveis no sistema",
            "parameters": {
                "page": {"type": "number", "description": "Número da página (padrão: 1)"},
                "per_page": {"type": "number", "description": "Itens por página (padrão: 15, máx: 100)"}
            }
        },
        {
            "name": "get_agent",
            "description": "Obtém detalhes de um agente específico",
            "parameters": {
                "agent_id": {"type": "string", "description": "ID do agente a ser consultado"}
            }
        },
        {
            "name": "execute_agent",
            "description": "Executa um agente com mensagens específicas",
            "parameters": {
                "agent_id": {"type": "string", "description": "ID do agente a ser executado"},
                "model": {"type": "string", "description": "Modelo a ser usado (opcional)"},
                "tools": {"type": "array", "description": "Ferramentas a serem habilitadas (opcional)"},
                "messages": {"type": "array", "description": "Mensagens para o agente (formato chat JSON)"},
                "file_ids": {"type": "array", "description": "IDs dos arquivos a serem anexados (opcional)"},
                "temperature": {"type": "number", "description": "Temperatura para geração (0-1, padrão: 0.7)"},
                "wait_execution": {"type": "boolean", "description": "Esperar pela execução completa (padrão: true)"}
            }
        },
        {
            "name": "list_agent_files",
            "description": "Lista arquivos associados a um agente",
            "parameters": {
                "agent_id": {"type": "string", "description": "ID do agente"},
                "page": {"type": "number", "description": "Número da página (padrão: 1)"},
                "per_page": {"type": "number", "description": "Itens por página (padrão: 15, máx: 100)"}
            }
        }
    ]
    
    return {"tools": tools}

@app.post("/api/mcp/execute")
async def execute_tool(request: Request):
    """Executa uma ferramenta MCP"""
    session_id = request.query_params.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id não fornecido")
    
    # Parsear o corpo da requisição
    try:
        body = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Corpo da requisição inválido")
    
    tool_name = body.get("tool")
    params = body.get("params", {})
    
    if not tool_name:
        raise HTTPException(status_code=400, detail="Nome da ferramenta não fornecido")
    
    # Executar a ferramenta correspondente
    try:
        if tool_name == "health_check":
            result = await MCPTools.health_check()
            return {"body": json.dumps(result)}
        
        elif tool_name == "search_info":
            query = params.get("query")
            if not query:
                raise HTTPException(status_code=400, detail="Parâmetro 'query' não fornecido")
            
            result = await MCPTools.search_info(query)
            return {"body": result}
        
        elif tool_name == "process_image":
            url = params.get("url")
            if not url:
                raise HTTPException(status_code=400, detail="Parâmetro 'url' não fornecido")
            
            result = await MCPTools.process_image(url)
            return {"body": json.dumps(result)}
        
        elif tool_name == "chat_completion":
            prompt = params.get("prompt")
            if not prompt:
                raise HTTPException(status_code=400, detail="Parâmetro 'prompt' não fornecido")
            
            history = params.get("history", [])
            result = await MCPTools.chat_completion(prompt, history)
            return {"body": result}
        
        elif tool_name == "list_agents":
            page = int(params.get("page", 1))
            per_page = min(int(params.get("per_page", 15)), 100)  # Limita a 100 por página
            result = await MCPTools.list_agents(page, per_page)
            return {"body": json.dumps(result)}
        
        elif tool_name == "get_agent":
            agent_id = params.get("agent_id")
            if not agent_id:
                raise HTTPException(status_code=400, detail="Parâmetro 'agent_id' não fornecido")
            
            result = await MCPTools.get_agent(agent_id)
            return {"body": json.dumps(result)}
        
        elif tool_name == "execute_agent":
            agent_id = params.get("agent_id")
            if not agent_id:
                raise HTTPException(status_code=400, detail="Parâmetro 'agent_id' não fornecido")
            
            messages = params.get("messages")
            if not messages:
                raise HTTPException(status_code=400, detail="Parâmetro 'messages' não fornecido")
            
            model = params.get("model", "default")
            tools = params.get("tools", [])
            file_ids = params.get("file_ids", [])
            temperature = float(params.get("temperature", 0.7))
            wait_execution = bool(params.get("wait_execution", True))
            
            result = await MCPTools.execute_agent(
                agent_id, model, tools, messages, file_ids, temperature, wait_execution
            )
            return {"body": json.dumps(result)}
        
        elif tool_name == "list_agent_files":
            agent_id = params.get("agent_id")
            if not agent_id:
                raise HTTPException(status_code=400, detail="Parâmetro 'agent_id' não fornecido")
            
            page = int(params.get("page", 1))
            per_page = min(int(params.get("per_page", 15)), 100)  # Limita a 100 por página
            
            result = await MCPTools.list_agent_files(agent_id, page, per_page)
            return {"body": json.dumps(result)}
        
        else:
            raise HTTPException(status_code=404, detail=f"Ferramenta '{tool_name}' não encontrada")
    
    except Exception as e:
        logger.error(f"Erro ao executar ferramenta {tool_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao executar ferramenta MCP: {str(e)}")

# ----- Iniciar o servidor -----

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "3000"))
    logger.info(f"Iniciando servidor TESS MCP na porta {port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port) 