#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import signal
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

# Flag global para controlar o encerramento gracioso
shutdown_requested = False

# Manipulador de sinal para encerramento gracioso
def signal_handler():
    global shutdown_requested
    shutdown_requested = True
    print("\nEncerrando graciosamente. Aguarde...")

async def run_agent(message: str) -> None:
    """Execute o agente com a mensagem fornecida usando o modelo Arcee e as ferramentas MCP."""
    
    # Verificar se as variáveis de ambiente necessárias estão configuradas
    required_vars = ["ARCEE_API_KEY", "ARCEE_APP_URL", "DATABUTTON_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Erro: As seguintes variáveis de ambiente são necessárias: {', '.join(missing_vars)}")
        print("Por favor, configure-as antes de executar o script.")
        return
    
    # Configurar manipuladores de sinal para encerramento gracioso
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)
    
    mcp_tools = None
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
            
            # Verificar se foi solicitado encerramento antes de iniciar
            if shutdown_requested:
                print("Encerramento solicitado antes de iniciar o processamento")
                return
            
            # Executar o agente com timeout e tratamento mais robusto
            try:
                # Definir um timeout para evitar bloqueios indefinidos
                timeout = 120  # 2 minutos
                
                # Primeiro tente com streaming
                stream_success = False
                try:
                    # Usar wait_for para adicionar timeout
                    await asyncio.wait_for(
                        agent.aprint_response(message, stream=True),
                        timeout=timeout
                    )
                    stream_success = True
                except asyncio.TimeoutError:
                    print(f"\nTimeout ao processar a mensagem em modo streaming após {timeout} segundos.")
                except Exception as e:
                    print(f"\nErro no modo streaming: {e}. Tentando sem streaming...")
                
                # Se o streaming falhar e não foi solicitado encerramento, use o modo normal
                if not stream_success and not shutdown_requested:
                    try:
                        # Usar wait_for para adicionar timeout
                        response = await asyncio.wait_for(
                            agent.agenerate_response(message),
                            timeout=timeout
                        )
                        print(response.content)
                    except asyncio.TimeoutError:
                        print(f"\nTimeout ao processar a mensagem em modo normal após {timeout} segundos.")
                
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
    
    finally:
        # Garantir que todos os recursos sejam liberados adequadamente
        if mcp_tools:
            try:
                # Não é necessário fechar de novo se já estiver no bloco with
                pass
            except Exception as e:
                print(f"Erro ao fechar MCP Tools: {e}")
                
        print("Servidor MCP encerrado.")

# Ponto de entrada
if __name__ == "__main__":
    # Verificar se um argumento foi fornecido na linha de comando
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        # Exemplo básico se nenhum argumento for fornecido
        query = "Quais ferramentas você tem à sua disposição e como posso usá-las para analisar dados?"
        
    print(f"Executando agente com a consulta: '{query}'")
    
    try:
        # Executar com proteção contra cancelamentos e timeouts
        asyncio.run(run_agent(query))
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário. Encerrando...")
    except Exception as e:
        print(f"Erro fatal no programa: {e}")
        import traceback
        traceback.print_exc() 