#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import signal
import subprocess
from dotenv import load_dotenv
from textwrap import dedent
import time

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

class MCPServerManager:
    """Gerencia o ciclo de vida do servidor MCP."""
    
    def __init__(self, env_vars=None):
        self.env_vars = env_vars or {}
        self.mcp_process = None
        self.connection_attempts = 0
        self.max_attempts = 3
    
    def start_server(self):
        """Inicia o servidor MCP como um processo separado."""
        if self.mcp_process is not None and self.mcp_process.poll() is None:
            print("Servidor MCP já está em execução")
            return
        
        env = os.environ.copy()
        env.update(self.env_vars)
        
        try:
            print("Iniciando servidor MCP como processo separado...")
            self.mcp_process = subprocess.Popen(
                ["/home/agentsai/arcee_cli_agentes_tess/venv/bin/databutton-app-mcp"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"Servidor MCP iniciado com PID {self.mcp_process.pid}")
            # Pequena pausa para permitir que o servidor inicialize
            time.sleep(2)
            self.connection_attempts = 0
        except Exception as e:
            print(f"Erro ao iniciar o servidor MCP: {e}")
            self.mcp_process = None
    
    def stop_server(self):
        """Para o servidor MCP."""
        if self.mcp_process is not None and self.mcp_process.poll() is None:
            print(f"Parando servidor MCP (PID {self.mcp_process.pid})...")
            try:
                self.mcp_process.terminate()
                # Esperar até 5 segundos para encerrar graciosamente
                for _ in range(10):
                    if self.mcp_process.poll() is not None:
                        break
                    time.sleep(0.5)
                # Se ainda estiver rodando, forçar encerramento
                if self.mcp_process.poll() is None:
                    print("Forçando encerramento do servidor MCP...")
                    self.mcp_process.kill()
            except Exception as e:
                print(f"Erro ao parar o servidor MCP: {e}")
            finally:
                self.mcp_process = None
        else:
            print("Servidor MCP não está em execução")
    
    def check_server(self):
        """Verifica se o servidor MCP está rodando."""
        if self.mcp_process is not None:
            if self.mcp_process.poll() is None:
                return True
            else:
                return_code = self.mcp_process.poll()
                print(f"Servidor MCP encerrou com código {return_code}")
                self.mcp_process = None
                return False
        return False
    
    def restart_if_needed(self):
        """Reinicia o servidor MCP se necessário."""
        if not self.check_server() and self.connection_attempts < self.max_attempts:
            print(f"Tentativa de reconexão {self.connection_attempts + 1}/{self.max_attempts}")
            self.connection_attempts += 1
            self.start_server()
            return True
        return self.check_server()

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
    
    # Preparar variáveis de ambiente para o servidor MCP
    env_vars = {
        "DATABUTTON_API_KEY": os.getenv("DATABUTTON_API_KEY"),
        "ARCEE_API_KEY": os.getenv("ARCEE_API_KEY"),
        "ARCEE_APP_URL": os.getenv("ARCEE_APP_URL"),
        "ARCEE_MODEL": os.getenv("ARCEE_MODEL", "auto")
    }
    
    # Criar gerenciador do servidor MCP
    mcp_manager = MCPServerManager(env_vars)
    
    # Iniciar o servidor MCP como processo separado
    mcp_manager.start_server()
    
    try:
        # Verificar se o servidor está executando
        if not mcp_manager.check_server():
            print("Não foi possível iniciar o servidor MCP. Encerrando.")
            return
        
        print("Configurando parâmetros para conexão com o servidor MCP...")
        
        # Criar os parâmetros para a conexão com o servidor MCP
        server_params = StdioServerParameters(
            command=None,  # Não precisamos iniciar outro processo, já temos um rodando
            open_stdio=False,  # Não queremos abrir novo stdio
            env=env_vars,
            # Por segurança, não fechar quando o objeto MCPTools for destruído
            exit_on_close=False  
        )

        # Inicializar o modelo Arcee
        arcee_model = ArceeModel(
            model=os.getenv("ARCEE_MODEL", "auto"),
            temperature=0.7,
            max_tokens=2000,
            debug=True
        )
        
        print("Modelo Arcee inicializado com sucesso")
        
        # Inicializar as ferramentas MCP
        print("Conectando às ferramentas MCP...")
        
        mcp_tools = None
        try:
            # Tentar conectar ao servidor MCP
            mcp_tools = MCPTools(server_params=server_params)
            await mcp_tools.__aenter__()
            print("Ferramentas MCP inicializadas com sucesso")
            
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
            print(f"Erro ao conectar com as ferramentas MCP: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Fechar a conexão com as ferramentas MCP
            if mcp_tools is not None:
                try:
                    await mcp_tools.__aexit__(None, None, None)
                except Exception as e:
                    print(f"Erro ao fechar a conexão com as ferramentas MCP: {e}")
            
    except Exception as e:
        print(f"Erro ao executar o agente: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Encerrar o servidor MCP
        mcp_manager.stop_server()
        print("Sessão do agente encerrada.")

# Repetir o processamento de mensagens
async def run_interactive_session():
    """Executa uma sessão interativa, permitindo múltiplas consultas."""
    while True:
        if shutdown_requested:
            print("Encerrando sessão interativa...")
            break
        
        try:
            # Obter consulta do usuário
            query = input("\nDigite sua pergunta (ou 'exit' para sair): ")
            
            # Verificar se o usuário quer sair
            if query.lower() in ('exit', 'quit', 'sair'):
                break
            
            # Executar agente com a consulta
            await run_agent(query)
            
        except KeyboardInterrupt:
            print("\nOperação interrompida pelo usuário.")
            if not shutdown_requested:
                signal_handler()  # Solicitar encerramento gracioso
            break
        except Exception as e:
            print(f"Erro na sessão interativa: {e}")
            import traceback
            traceback.print_exc()
            # Continuar para a próxima iteração
    
    print("Sessão interativa encerrada.")

# Ponto de entrada
if __name__ == "__main__":
    # Verificar se um argumento foi fornecido na linha de comando
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        
        print(f"Executando agente com a consulta: '{query}'")
        try:
            # Executar uma única consulta
            asyncio.run(run_agent(query))
        except KeyboardInterrupt:
            print("\nPrograma interrompido pelo usuário. Encerrando...")
        except Exception as e:
            print(f"Erro fatal no programa: {e}")
            import traceback
            traceback.print_exc()
    else:
        # Modo interativo - permite múltiplas consultas
        print("Iniciando modo interativo. Digite 'exit' para sair.")
        try:
            # Executar modo interativo
            asyncio.run(run_interactive_session())
        except KeyboardInterrupt:
            print("\nPrograma interrompido pelo usuário. Encerrando...")
        except Exception as e:
            print(f"Erro fatal no programa: {e}")
            import traceback
            traceback.print_exc() 