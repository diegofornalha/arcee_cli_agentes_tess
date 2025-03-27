from mcp.server.fastmcp import FastMCP

# Criar servidor MCP com nome
app = FastMCP("ServidorMinimo")

@app.tool()
async def echo(text: str) -> str:
    """Simplesmente retorna o texto informado"""
    return f"Você disse: {text}"

# Iniciar o servidor
if __name__ == "__main__":
    print("Iniciando servidor MCP na porta 8000...")
    app.run() 