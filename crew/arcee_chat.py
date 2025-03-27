#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comando para chat com o Arcee AI usando TESS
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.box import ROUNDED
from rich.prompt import Prompt
from rich import print
from infrastructure.providers.arcee_provider import ArceeProvider
from dotenv import load_dotenv

# Importar o processador de linguagem natural do TESS (se disponível)
try:
    from src.tools.mcp_nl_processor import MCPNLProcessor
    MCP_NL_PROCESSOR_AVAILABLE = True
except ImportError:
    MCP_NL_PROCESSOR_AVAILABLE = False

# Importar funcionalidades de teste da API TESS (se disponível)
try:
    from tests.test_api_tess import listar_agentes, executar_agente
    TEST_API_TESS_AVAILABLE = True
except ImportError:
    TEST_API_TESS_AVAILABLE = False

# Configurar logging
logger = logging.getLogger("arcee_chat")
logger.setLevel(logging.INFO)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter('INFO: %(message)s')
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)

# Handler para arquivo (opcional)
try:
    log_dir = os.path.expanduser("~/.arcee/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "arcee.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
except Exception as e:
    print(f"[yellow]Aviso:[/yellow] Não foi possível configurar o log em arquivo: {e}")

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da interface
console = Console()

def chat() -> None:
    """Inicia um chat com o Arcee AI usando o modo AUTO"""
    
    # Log de inicialização
    logger.info("Sistema de logging configurado. Arquivo de log: ~/.arcee/logs/arcee.log")
    if MCP_NL_PROCESSOR_AVAILABLE:
        logger.info("Módulo MCPNLProcessor disponível")
    else:
        logger.info("Módulo MCPNLProcessor não disponível")
    
    if TEST_API_TESS_AVAILABLE:
        logger.info("Módulo test_api_tess disponível")
    else:
        logger.info("Módulo test_api_tess não disponível")
    
    logger.info("Iniciando chat com Arcee AI")
    
    # Inicializar processador de linguagem natural do TESS
    mcp_nl_processor = None
    if MCP_NL_PROCESSOR_AVAILABLE:
        try:
            mcp_nl_processor = MCPNLProcessor()
            logger.info("Processador de linguagem natural do TESS carregado")
        except Exception as e:
            logger.error(f"Erro ao inicializar MCPNLProcessor: {e}")
    
    # Interface inicial
    console.print(
        Panel(
            "🤖 [bold]Chat com Arcee AI - Modo AUTO[/bold]\n\n"
            "Este chat utiliza o modo AUTO para selecionar automaticamente o melhor modelo\n"
            "com base no conteúdo e contexto da sua pergunta.\n\n"
            "Digite 'sair' para encerrar ou 'limpar' para reiniciar a conversa.",
            box=ROUNDED,
            title="Arcee AI",
            border_style="blue"
        )
    )

    # Verificar se a chave API está configurada
    api_key = os.getenv("ARCEE_API_KEY")
    if not api_key:
        console.print("[bold red]Erro:[/bold red] ARCEE_API_KEY não configurada. Configure no arquivo .env")
        sys.exit(1)

    try:
        # Inicializar o provedor Arcee com modo AUTO
        provider = ArceeProvider()
        
        # Verificar conexão
        status, message = provider.health_check()
        if status:
            console.print("[green]✓ Conexão com Arcee AI estabelecida[/green]")
            if provider.model == "auto":
                console.print("[green]✓ Modo AUTO ativado - seleção dinâmica de modelo[/green]")
            else:
                console.print(f"[green]✓ Modelo fixo: {provider.model}[/green]")
        else:
            console.print(f"[yellow]⚠ Arcee indisponível: {message}[/yellow]")
            sys.exit(1)
            
        # Lista para armazenar histórico de mensagens
        messages = []

        # Loop principal do chat
        while True:
            try:
                # Obter entrada do usuário
                user_input = Prompt.ask("\n[bold blue]Você[/bold blue]")

                # Comandos especiais
                if user_input.lower() == "sair":
                    logger.info("Detectado comando básico: sair")
                    console.print("[yellow]Encerrando chat...[/yellow]")
                    break
                    
                if user_input.lower() == "limpar":
                    logger.info("Detectado comando básico: limpar")
                    messages = []
                    console.print("[green]✓ Histórico limpo[/green]")
                    continue
                    
                if user_input.lower() in ["ajuda", "help", "?"]:
                    logger.info("Detectado comando básico: ajuda")
                    _mostrar_ajuda(console)
                    continue
                    
                if user_input.lower() == "modelos":
                    logger.info("Detectado comando básico: modelos")
                    if provider.model_usage_stats:
                        console.print("[bold]Estatísticas de uso de modelos:[/bold]")
                        for model, count in provider.model_usage_stats.items():
                            console.print(f"• {model}: {count} vezes")
                    else:
                        console.print("[italic]Nenhum modelo foi usado ainda nesta sessão[/italic]")
                    continue
                
                # Verificar comandos TESS via test_api_tess
                tess_response = None
                if TEST_API_TESS_AVAILABLE and user_input.startswith("test_api_tess"):
                    args = user_input.split()
                    if len(args) >= 2:
                        if args[1].lower() == "listar":
                            logger.info("Detectado comando do TESS: listar_agentes")
                            console.print("[italic]Executando comando TESS: listar agentes...[/italic]")
                            success, data = listar_agentes(is_cli=False)
                            if success:
                                console.print("[green]✓ Comando TESS executado com sucesso[/green]")
                                # Formatar a resposta para exibição no chat
                                tess_response = f"[bold]Agentes TESS disponíveis:[/bold]\n\n"
                                for i, agent in enumerate(data.get('data', [])[:5], 1):
                                    tess_response += f"{i}. [bold]{agent.get('title', 'Sem título')}[/bold]\n"
                                    tess_response += f"   ID: {agent.get('slug', 'N/A')}\n"
                                    tess_response += f"   {agent.get('description', 'Sem descrição')}\n\n"
                                tess_response += f"Total: {data.get('total', 0)} agentes disponíveis"
                            else:
                                tess_response = f"[bold red]Erro ao listar agentes TESS:[/bold red] {data.get('error', 'Erro desconhecido')}"
                        
                        elif args[1].lower() == "executar" and len(args) >= 4:
                            agent_id = args[2]
                            mensagem = " ".join(args[3:])
                            logger.info(f"Detectado comando da API TESS: executar_agente {agent_id}")
                            console.print(f"[italic]Executando agente TESS {agent_id}...[/italic]")
                            success, data = executar_agente(agent_id, mensagem, is_cli=False)
                            if success and "output" in data:
                                console.print("[green]✓ Agente TESS executado com sucesso[/green]")
                                tess_response = f"[bold]Resposta do agente TESS ({agent_id}):[/bold]\n\n{data['output']}"
                            else:
                                error_msg = data.get('error', 'Erro desconhecido')
                                tess_response = f"[bold red]Erro ao executar agente TESS:[/bold red] {error_msg}"
                    
                    if tess_response:
                        console.print(f"\n[bold green]Assistente:[/bold green] {tess_response}")
                        # Adicionar à história de conversa
                        messages.append({"role": "user", "content": user_input})
                        messages.append({"role": "assistant", "content": tess_response})
                        continue
                
                # Verificar comandos do MCPNLProcessor
                if mcp_nl_processor:
                    is_comando, tipo_comando, params = mcp_nl_processor.detectar_comando(user_input)
                    if is_comando:
                        logger.info(f"Detectado comando do TESS: {tipo_comando}")
                        console.print(f"[italic]Processando comando TESS: {tipo_comando}...[/italic]")
                        try:
                            resposta = mcp_nl_processor.processar_comando(tipo_comando, params)
                            if resposta:
                                # Verificar o tipo de comando para formatação especial
                                if tipo_comando in ["listar_todos_agentes", "listar_agentes"]:
                                    # Limitar resposta para não sobrecarregar a interface
                                    lines = resposta.split('\n')
                                    limited_response = '\n'.join(lines[:100]) + '\n...' if len(lines) > 100 else resposta
                                    console.print(f"\n[bold green]Assistente:[/bold green]")
                                    console.print(Panel(limited_response, title="Agentes TESS", border_style="green"))
                                else:
                                    console.print(f"\n[bold green]Assistente:[/bold green] {resposta}")
                                
                                # Adicionar à história de conversa
                                messages.append({"role": "user", "content": user_input})
                                messages.append({"role": "assistant", "content": resposta})
                                continue
                        except Exception as e:
                            logger.error(f"Erro ao processar comando TESS: {e}")
                            console.print(f"[bold red]Erro ao processar comando TESS:[/bold red] {str(e)}")
                            continue

                # Comandos básicos do chat
                basic_command = False
                if user_input.lower() == "sair":
                    logger.info("Detectado comando básico: sair")
                    basic_command = True
                elif user_input.lower() == "limpar":
                    logger.info("Detectado comando básico: limpar")
                    basic_command = True
                elif user_input.lower() in ["ajuda", "help", "?"]:
                    logger.info("Detectado comando básico: ajuda")
                    basic_command = True
                elif user_input.lower() == "modelos":
                    logger.info("Detectado comando básico: modelos")
                    basic_command = True

                if not basic_command:
                    # Mostrar indicador de processamento
                    console.print("[italic]Processando...[/italic]", end="\r")
                    
                     
                    # Adicionar mensagem ao histórico
                    messages.append({"role": "user", "content": user_input})
                    
                    # Gerar resposta
                    response = provider.generate_content_chat(messages)

                    # Limpar linha do "Processando..."
                    console.print(" " * 30, end="\r")

                    # Verificar se houve erro
                    if "error" in response:
                        console.print(f"[bold red]Erro:[/bold red] {response['error']}")
                        continue

                    # Extrair o texto da resposta
                    assistant_message = response["text"]
                    
                    # Extrair o modelo usado
                    model_used = response.get("selected_model", "desconhecido")

                    # Mostrar resposta
                    console.print(f"\n[bold green]Assistente:[/bold green] {assistant_message}")
                    
                    # Mostrar informação sobre o modelo usado
                    if model_used:
                        console.print(f"[dim italic](Resposta gerada pelo modelo: {model_used})[/dim italic]")
                    
                    # Adicionar resposta ao histórico
                    messages.append({"role": "assistant", "content": assistant_message})

            except KeyboardInterrupt:
                console.print("\n[yellow]Interrompido pelo usuário.[/yellow]")
                break
            except Exception as e:
                console.print(f"[bold red]Erro:[/bold red] {str(e)}")
                continue

        console.print("\nAté logo! 👋")

    except Exception as e:
        console.print(f"[bold red]Erro durante inicialização:[/bold red] {str(e)}")
        sys.exit(1)

def _mostrar_ajuda(console):
    """Exibe ajuda detalhada sobre comandos disponíveis"""
    console.print(Panel(
        "[bold blue]Comandos Disponíveis[/bold blue]",
        box=ROUNDED,
        border_style="blue"
    ))
    
    # Comandos básicos
    console.print("[bold]Comandos gerais:[/bold]")
    console.print("• [bold]ajuda[/bold] - Mostra esta mensagem")
    console.print("• [bold]limpar[/bold] - Limpa o histórico da conversa")
    console.print("• [bold]sair[/bold] - Encerra o chat")
    console.print("• [bold]modelos[/bold] - Mostra estatísticas dos modelos usados no modo AUTO")
    
    # Comandos TESS API
    if TEST_API_TESS_AVAILABLE:
        console.print("\n[bold]Comandos TESS API:[/bold]")
        console.print("• [bold]test_api_tess listar[/bold] - Lista agentes TESS disponíveis")
        console.print("• [bold]test_api_tess executar <id> <mensagem>[/bold] - Executa um agente TESS específico")
    
    # Comandos específicos do Arcee
    console.print("\n[bold]Dicas de uso:[/bold]")
    console.print("• Para tarefas criativas, use frases como 'criar', 'escrever' ou 'imaginar'")
    console.print("• Para consultas técnicas, seja específico sobre tecnologias")
   
if __name__ == "__main__":
    chat() 