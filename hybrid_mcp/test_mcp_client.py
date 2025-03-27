from mcp.client.session import ClientSession
import asyncio

async def main():
    # Criar sessão de cliente MCP
    async with ClientSession(
        api_url="http://localhost:8000"
    ) as session:
        print("Conectando ao servidor MCP...")
        
        try:
            # Testar a ferramenta echo
            response = await session.call_tool("echo", {"text": "Olá, mundo!"})
            print(f"Resposta: {response}")
            
            print("Teste concluído com sucesso!")
        except Exception as e:
            print(f"Erro ao testar o servidor MCP: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 