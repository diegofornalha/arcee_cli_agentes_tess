import asyncio
import os
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime
import json

from mcp.server.fastmcp import FastMCP, Context, Image
from rust_backend import create_rust_client

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("hybrid-mcp")

# Servidor MCP principal em Python
mcp = FastMCP("ChatHíbrido")

# Configuração do cliente Rust
RUST_BACKEND_URL = os.environ.get("RUST_BACKEND_URL", "http://localhost:3000")
rust_client = create_rust_client(RUST_BACKEND_URL)

# ----- Implementações Python nativas -----

async def fetch_chat_history_python(chat_id: str) -> str:
    """Implementação Python para buscar histórico de chat"""
    # Simula busca de histórico (em produção, conectaria ao seu banco de dados)
    logger.info(f"Buscando histórico do chat {chat_id} usando backend Python")
    # Simula um atraso de rede
    await asyncio.sleep(0.2)
    return f"Histórico do chat {chat_id} (via Python): Última mensagem em {datetime.now().isoformat()}"

async def search_info_python(query: str) -> str:
    """Implementação Python para busca de informações"""
    logger.info(f"Buscando informações sobre '{query}' usando backend Python")
    # Simula busca (em produção, usaria uma API real)
    await asyncio.sleep(0.5)
    return f"Resultados para '{query}' (via Python): Encontradas 5 referências relevantes."

# ----- Recursos MCP -----

@mcp.resource("chat_history://{chat_id}")
async def get_chat_history(chat_id: str) -> str:
    """Recurso MCP para histórico de chat com fallback"""
    try:
        # Tenta usar o backend Python primeiro
        return await fetch_chat_history_python(chat_id)
    except Exception as e:
        # Registra o erro
        logger.warning(f"Fallback para Rust devido a: {str(e)}")
        
        try:
            # Fallback para o backend Rust
            return await rust_client.get_chat_history(chat_id)
        except Exception as rust_error:
            # Se ambos falharem, loga o erro e retorna mensagem amigável
            logger.error(f"Ambos os backends falharam. Rust: {str(rust_error)}")
            return f"Não foi possível recuperar o histórico do chat {chat_id} no momento."

@mcp.resource("user_profile://{user_id}")
async def get_user_profile(user_id: str) -> str:
    """Recurso MCP para perfil de usuário"""
    # Apenas implementação Python por simplicidade
    return f"Perfil do usuário {user_id}: Membro desde Janeiro 2024"

# ----- Ferramentas MCP -----

@mcp.tool()
async def buscar_informacao(query: str) -> str:
    """Busca informações com fallback para Rust"""
    try:
        # Tenta usar o backend Python primeiro
        return await search_info_python(query)
    except Exception as e:
        # Registra o erro e notifica o cliente
        logger.warning(f"Fallback para Rust devido a: {str(e)}")
        
        try:
            # Fallback para o backend Rust
            return await rust_client.search_info(query)
        except Exception as rust_error:
            # Se ambos falharem, loga o erro e retorna mensagem amigável
            logger.error(f"Ambos os backends falharam. Rust: {str(rust_error)}")
            return f"Não foi possível buscar informações sobre '{query}' no momento."

@mcp.tool()
async def processar_imagem(image_url: str) -> str:
    """Processamento de imagem (delegado principalmente ao Rust por desempenho)"""
    try:
        # Preferimos o backend Rust para processamento de imagem devido ao desempenho
        logger.info("Processando imagem via backend Rust otimizado")
        result = await rust_client.process_image(image_url)
        return json.dumps(result)
    except Exception as e:
        # Se o Rust falhar, log e retorno amigável (sem fallback para Python neste caso)
        logger.error(f"Falha no processamento de imagem: {str(e)}")
        return json.dumps({"error": "Não foi possível processar a imagem no momento."})

@mcp.tool()
async def chat_completion(prompt: str, history: Optional[list] = None) -> str:
    """Simulação de chat completion com balanceamento de carga"""
    # Decisão de balanceamento baseada em carga simples
    use_rust = len(prompt) > 100  # Envia prompts maiores para Rust (exemplo simples)
    
    if use_rust:
        logger.info("Direcionando para backend Rust devido ao tamanho do prompt")
        try:
            return await rust_client.call_rust_tool("chat_completion", {
                "prompt": prompt,
                "history": history or []
            })
        except Exception as e:
            # Fallback para Python em caso de erro
            logger.warning(f"Fallback para Python devido a: {str(e)}")
    
    # Implementação Python (ou fallback)
    logger.info(f"Processando chat completion via Python, prompt size: {len(prompt)}")
    await asyncio.sleep(0.3)  # Simula processamento
    return f"Resposta para: {prompt[:30]}... (via Python)"

# ----- Prompts MCP -----

@mcp.prompt()
def simple_chat(message: str) -> str:
    """Prompt simples para chat"""
    return f"Por favor, responda a seguinte mensagem de forma natural: {message}"

@mcp.prompt()
def image_analysis(image_url: str) -> str:
    """Prompt para análise de imagem"""
    return f"""
    Analise esta imagem em detalhes: {image_url}
    
    Por favor, descreva:
    1. O que você vê na imagem
    2. Cores e elementos principais
    3. Qualquer texto visível
    """

# ----- Inicialização do servidor -----

async def startup():
    """Função de inicialização chamada antes do servidor iniciar"""
    logger.info(f"Inicializando servidor MCP híbrido com backend Rust em {RUST_BACKEND_URL}")
    # Verificar conexão com backend Rust
    try:
        async with rust_client as client:
            await client.call_rust_tool("health_check", {})
        logger.info("Conexão com backend Rust estabelecida com sucesso")
    except Exception as e:
        logger.warning(f"Aviso: Backend Rust não está disponível: {str(e)}")
        logger.info("Continuando com funcionalidades Python apenas")

async def shutdown():
    """Função de encerramento chamada quando o servidor é desligado"""
    logger.info("Encerrando servidor MCP híbrido")
    # Qualquer limpeza necessária

# Iniciar servidor MCP
if __name__ == "__main__":
    try:
        # Executar startup de forma síncrona antes de iniciar o servidor
        import asyncio
        asyncio.run(startup())
        
        # Iniciar o servidor MCP
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro ao executar servidor MCP: {str(e)}") 