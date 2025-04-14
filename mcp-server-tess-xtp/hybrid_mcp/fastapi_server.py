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
logger = logging.getLogger("agno-mcp-python")

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