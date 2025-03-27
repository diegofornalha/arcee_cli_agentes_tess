import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional, Union

class RustBackendClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            self.session = None
    
    async def ensure_session(self):
        """Garante que existe uma sessão HTTP ativa"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def get_chat_history(self, chat_id: str) -> str:
        """Obtém histórico de chat via backend Rust"""
        await self.ensure_session()
        
        async with self.session.get(
            f"{self.base_url}/api/mcp/tools",
            params={"session_id": "internal", "resource": f"chat_history://{chat_id}"}
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("body", "")
            
            error_text = await resp.text()
            raise Exception(f"Erro no backend Rust: {resp.status} - {error_text}")
    
    async def search_info(self, query: str) -> str:
        """Pesquisa de informações via backend Rust"""
        await self.ensure_session()
        
        async with self.session.post(
            f"{self.base_url}/api/mcp/execute",
            json={"tool": "search_info", "params": {"query": query}},
            params={"session_id": "internal"}
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("body", "")
            
            error_text = await resp.text()
            raise Exception(f"Erro no backend Rust: {resp.status} - {error_text}")
    
    async def process_image(self, image_url: str) -> Dict[str, Any]:
        """Processamento de imagens via backend Rust (otimizado)"""
        await self.ensure_session()
        
        async with self.session.post(
            f"{self.base_url}/api/mcp/execute",
            json={"tool": "process_image", "params": {"url": image_url}},
            params={"session_id": "internal"}
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                try:
                    if isinstance(data.get("body"), str):
                        return json.loads(data.get("body", "{}"))
                    return data.get("body", {})
                except json.JSONDecodeError:
                    return {"error": "Formato de resposta inválido", "raw": data.get("body", "")}
            
            error_text = await resp.text()
            raise Exception(f"Erro no backend Rust: {resp.status} - {error_text}")
    
    async def call_rust_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Método genérico para chamar qualquer ferramenta do backend Rust"""
        await self.ensure_session()
        
        async with self.session.post(
            f"{self.base_url}/api/mcp/execute",
            json={"tool": tool_name, "params": params},
            params={"session_id": "internal"}
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("body", "")
            
            error_text = await resp.text()
            raise Exception(f"Erro ao chamar ferramenta {tool_name}: {resp.status} - {error_text}")

# Função auxiliar para criar um cliente
def create_rust_client(base_url: str = "http://localhost:3000") -> RustBackendClient:
    return RustBackendClient(base_url) 