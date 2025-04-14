import asyncio
import os
from dotenv import load_dotenv
from textwrap import dedent

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters

# Carregar variáveis de ambiente
load_dotenv()

# Obter a chave API do Agno
AGNO_API_KEY = os.getenv("AGNO_API_KEY")

async def run_agent(message: str) -> None:
    """Execute o agente com a mensagem fornecida."""
    
    # Parâmetros para o servidor MCP
    server_params = StdioServerParameters(
        command="/home/agentsai/venv/bin/databutton-app-mcp",
        env={
            "DATABUTTON_API_KEY": os.getenv("DATABUTTON_API_KEY")
        }
    )

    # Inicializar as ferramentas MCP
    async with MCPTools(server_params=server_params) as mcp_tools:
        agent = Agent(
            model=Claude(
                id="claude-3-5-sonnet-20240620", 
                api_key=os.getenv("ANTHROPIC_API_KEY")
            ),
            tools=[mcp_tools],
            instructions=dedent("""\
                Você é um assistente que pode acessar as ferramentas do Databutton.
                Use as ferramentas disponíveis para ajudar o usuário.
                
                - Responda de forma concisa e clara
                - Explique o que está fazendo
                - Use markdown para organizar suas respostas
            """),
            markdown=True,
            show_tool_calls=True,
        )

        # Executar o agente
        await agent.aprint_response(message, stream=True)

# Ponto de entrada
if __name__ == "__main__":
    # Exemplo básico
    asyncio.run(run_agent("Que ferramentas você tem à sua disposição?")) 