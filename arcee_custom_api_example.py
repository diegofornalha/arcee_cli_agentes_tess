import asyncio
import os
import traceback
from dotenv import load_dotenv
from textwrap import dedent

from agno.agent import Agent
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters

# Importar nossa implementação do modelo Arcee
from arcee_cli_agentes_tess.arcee_model import ArceeModel

# Carregar variáveis de ambiente
load_dotenv()

"""
# Nota sobre integração com Arcee API:
# Para integrar completamente a API da Arcee, seria necessário implementar uma classe personalizada
# que estenda Model e implemente todos os métodos abstratos necessários:
#
# class ArceeModel(Model):
#     - ainvoke
#     - ainvoke_stream
#     - invoke
#     - invoke_stream
#     - parse_provider_response
#     - parse_provider_response_delta
#
# Esta implementação exigiria um conhecimento detalhado da API e dos formatos de resposta da Arcee.
# Como alternativa mais simples, podemos usar um modelo suportado nativamente como o Claude
# e posteriormente explorar a criação de um adaptador completo para a Arcee.
"""

async def run_agent(message: str) -> None:
    """Execute o agente com a mensagem fornecida."""
    
    # Parâmetros para o servidor MCP
    server_params = StdioServerParameters(
        command="/home/agentsai/venv/bin/databutton-app-mcp",
        env={
            "DATABUTTON_API_KEY": os.getenv("DATABUTTON_API_KEY"),
            # Passamos as credenciais da Arcee para o servidor MCP
            "ARCEE_API_KEY": os.getenv("ARCEE_API_KEY"),
            "ARCEE_APP_URL": os.getenv("ARCEE_APP_URL"),
            "ARCEE_MODEL": os.getenv("ARCEE_MODEL")
        }
    )

    try:
        print("Inicializando integração com o modelo Arcee...")
        
        # Exibir informações de configuração para debugging
        print(f"URL da API Arcee: {os.getenv('ARCEE_APP_URL')}")
        print(f"Modelo Arcee: {os.getenv('ARCEE_MODEL')}")
        print(f"API Key Arcee: {os.getenv('ARCEE_API_KEY')[:8]}..." if os.getenv('ARCEE_API_KEY') else "Não definida")
        
        # Inicializar as ferramentas MCP
        async with MCPTools(server_params=server_params) as mcp_tools:
            print("Ferramentas MCP inicializadas com sucesso")
            
            # Configurar o modelo Arcee
            arcee_model = ArceeModel(
                # Parâmetros específicos para a API da Arcee
                temperature=0.7,
                max_tokens=2000,
                timeout=120.0,
                
                # Utilizamos o cliente OpenAI diretamente conforme implementado no arcee_cli_agentes_tess
                debug=True
            )
            
            print("Modelo Arcee configurado com sucesso")
            
            # Criar o agente com o modelo Arcee
            agent = Agent(
                model=arcee_model,
                tools=[mcp_tools],
                instructions=dedent("""\
                    Você é um assistente que pode acessar as ferramentas do Databutton.
                    Use as ferramentas disponíveis para ajudar o usuário.
                    
                    Você está conectado à API da Arcee, um serviço de modelo de linguagem 
                    personalizado que pode ser acessado em https://models.arcee.ai/v1.
                    
                    O modelo Arcee fornece:
                    - Respostas automáticas em português do Brasil
                    - Integração com ferramentas e APIs externas
                    - Sistema de seleção automática do melhor modelo para cada consulta
                    
                    - Responda de forma concisa e clara
                    - Explique o que está fazendo
                    - Use markdown para organizar suas respostas
                """),
                markdown=True,
                show_tool_calls=True,
            )
            
            print("Agente configurado com sucesso, processando mensagem...")
            
            # Executar o agente
            await agent.aprint_response(message, stream=True)
            
            # Mostrar estatísticas de uso do modelo após a execução
            if hasattr(arcee_model, 'model_usage_stats') and arcee_model.model_usage_stats:
                print("\nEstatísticas de uso de modelos Arcee:")
                for model, count in arcee_model.model_usage_stats.items():
                    print(f"- {model}: {count} vezes")
            
            if hasattr(arcee_model, 'last_model_used') and arcee_model.last_model_used:
                print(f"\nÚltimo modelo usado: {arcee_model.last_model_used}")
                
    except Exception as e:
        print(f"Erro ao executar o agente: {e}")
        print(f"Detalhes do erro:\n{traceback.format_exc()}")
        # Fallback para modelo Claude em caso de erro
        print("\nUsando Claude como fallback devido a erro na integração com Arcee...\n")
        
        # Reiniciar as ferramentas MCP
        async with MCPTools(server_params=server_params) as mcp_tools:
            from agno.models.anthropic import Claude
            
            claude_model = Claude(
                id="claude-3-5-sonnet-20240620", 
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            
            agent = Agent(
                model=claude_model,
                tools=[mcp_tools],
                instructions=dedent("""\
                    Você é um assistente que pode acessar as ferramentas do Databutton.
                    Use as ferramentas disponíveis para ajudar o usuário.
                    
                    Você também tem conhecimento sobre a API da Arcee, que é uma API personalizada
                    para modelos de linguagem. Quando perguntado sobre a Arcee API, explique que
                    é uma API de modelo de linguagem customizada que pode ser acessada em:
                    https://models.arcee.ai/v1
                    
                    - Responda de forma concisa e clara
                    - Explique o que está fazendo
                    - Use markdown para organizar suas respostas
                """),
                markdown=True,
                show_tool_calls=True,
            )
            
            # Executar o agente com Claude como fallback
            await agent.aprint_response(message, stream=True)

# Ponto de entrada
if __name__ == "__main__":
    # Exemplo básico
    asyncio.run(run_agent("O que você pode fazer com o modelo da Arcee?")) 