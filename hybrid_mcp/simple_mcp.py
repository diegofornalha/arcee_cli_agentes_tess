import asyncio
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from mcp.server.fastmcp import FastMCP

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("simple-mcp")

# Servidor MCP simples
mcp = FastMCP("MCPSimples")

# ----- Ferramentas MCP -----

@mcp.tool()
async def buscar_informacao(query: str) -> str:
    """Busca informações sobre um tópico"""
    logger.info(f"Buscando informações sobre '{query}'")
    # Simula um processamento
    await asyncio.sleep(0.5)
    return f"Resultados para '{query}': Encontradas 5 referências relevantes em {datetime.now().isoformat()}"

@mcp.tool()
async def processar_imagem(image_url: str) -> str:
    """Processa uma imagem e retorna informações sobre ela"""
    logger.info(f"Processando imagem em {image_url}")
    # Simula processamento
    await asyncio.sleep(1)
    result = {
        "width": 800,
        "height": 600,
        "format": "jpeg",
        "has_faces": True,
        "description": f"Imagem em {image_url} processada com sucesso",
        "tags": ["imagem", "processada", "teste"]
    }
    return str(result)

@mcp.tool()
async def chat_completion(prompt: str, history: Optional[list] = None) -> str:
    """Simula uma resposta de chat completion"""
    logger.info(f"Processando chat completion, prompt size: {len(prompt)}")
    # Simula processamento
    await asyncio.sleep(0.3)
    return f"Resposta para: {prompt[:30]}... (gerada em {datetime.now().isoformat()})"

# ----- Iniciar servidor MCP -----

if __name__ == "__main__":
    try:
        # Iniciar o servidor MCP
        port = int(os.environ.get("PORT", "8000"))
        logger.info(f"Iniciando servidor MCP na porta {port}")
        
        # Definir a porta via variável de ambiente conforme recomendado pelo MCP
        os.environ["PORT"] = str(port)
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro ao executar servidor MCP: {str(e)}") 