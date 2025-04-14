#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
from dotenv import load_dotenv
from textwrap import dedent

from agno.agent import Agent
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters

# Importar o modelo Arcee
sys.path.append('/home/agentsai')
from arcee_model import ArceeModel

# Carregar variáveis de ambiente
load_dotenv()

async def run_agent(message: str) -> None:
    """Execute o agente com a mensagem fornecida usando o modelo Arcee e as ferramentas MCP."""
    
    # Verificar se as variáveis de ambiente necessárias estão configuradas
    required_vars = ["ARCEE_API_KEY", "ARCEE_APP_URL", "DATABUTTON_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Erro: As seguintes variáveis de ambiente são necessárias: {', '.join(missing_vars)}")
        print("Por favor, configure-as antes de executar o script.")
        return
    
    try:
        # Parâmetros para o servidor MCP
        server_params = StdioServerParameters(
            command="/home/agentsai/arcee_cli_agentes_tess/venv/bin/databutton-app-mcp",
            env={
                "DATABUTTON_API_KEY": os.getenv("DATABUTTON_API_KEY"),
                # Passando as credenciais da Arcee para o servidor MCP
                "ARCEE_API_KEY": os.getenv("ARCEE_API_KEY"),
                "ARCEE_APP_URL": os.getenv("ARCEE_APP_URL"),
                "ARCEE_MODEL": os.getenv("ARCEE_MODEL", "auto")
            }
        )

        print("Inicializando servidor MCP...")
        
        # Inicializar as ferramentas MCP
        async with MCPTools(server_params=server_params) as mcp_tools:
            print("Ferramentas MCP inicializadas com sucesso")
            
            # Inicializar o modelo Arcee
            arcee_model = ArceeModel(
                model=os.getenv("ARCEE_MODEL", "auto"),
                temperature=0.7,
                max_tokens=2000,
                debug=True
            )
            
            print("Modelo Arcee inicializado com sucesso")
            
            # Criar o agente com o modelo Arcee e as ferramentas MCP
            agent = Agent(
                model=arcee_model,
                tools=[mcp_tools],
                instructions=dedent("""\
                    Você é um assistente que utiliza a API da Arcee e pode acessar as ferramentas do Databutton.
                    
                    Suas respostas devem ser:
                    - Claras e objetivas
                    - Culturalmente apropriadas para o contexto brasileiro
                    - Bem estruturadas e organizadas
                    - Profissionais mas amigáveis
                    
                    Use as ferramentas disponíveis quando necessário para ajudar o usuário.
                    Use markdown para formatar suas respostas quando apropriado.
                """),
                markdown=True,
                show_tool_calls=True,
            )
            
            print("Agente configurado com sucesso, processando mensagem...")
            
            # Executar o agente
            try:
                # Primeiro tente com streaming
                stream_success = False
                try:
                    await agent.aprint_response(message, stream=True)
                    stream_success = True
                except Exception as e:
                    print(f"\nErro no modo streaming: {e}. Tentando sem streaming...")
                
                # Se o streaming falhar, use o modo normal
                if not stream_success:
                    response = await agent.agenerate_response(message)
                    print(response.content)
                
                # Mostrar estatísticas de uso do modelo após a execução
                if hasattr(arcee_model, 'model_usage_stats') and arcee_model.model_usage_stats:
                    print("\nEstatísticas de uso de modelos Arcee:")
                    for model, count in arcee_model.model_usage_stats.items():
                        print(f"- {model}: {count} vezes")
                
                if hasattr(arcee_model, 'last_model_used') and arcee_model.last_model_used:
                    print(f"\nÚltimo modelo usado: {arcee_model.last_model_used}")
            except Exception as e:
                print(f"Erro ao gerar resposta: {e}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"Erro ao executar o agente: {e}")
        import traceback
        traceback.print_exc()

# Ponto de entrada
if __name__ == "__main__":
    # Verificar se um argumento foi fornecido na linha de comando
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        # Exemplo básico se nenhum argumento for fornecido
        query = "Quais ferramentas você tem à sua disposição e como posso usá-las para analisar dados?"
        
    print(f"Executando agente com a consulta: '{query}'")
    asyncio.run(run_agent(query)) 