#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comando para chat com o Arcee AI usando TESS
"""

import os
import sys
import logging
import re
import json
import urllib.parse
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.box import ROUNDED
from rich.prompt import Prompt
from rich import print
from infrastructure.providers.arcee_provider import ArceeProvider
from dotenv import load_dotenv

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

# Função para verificar se o módulo test_api_tess está disponível
def is_test_api_tess_available():
    try:
        from tests.test_api_tess import listar_agentes, executar_agente
        return True
    except ImportError:
        try:
            # Adicionar diretório raiz ao path e tentar novamente
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from tests.test_api_tess import listar_agentes, executar_agente
            return True
        except ImportError:
            return False

# Função para verificar se o MCPNLProcessor está disponível
def is_mcp_nl_processor_available():
    try:
        from src.tools.mcp_nl_processor import MCPNLProcessor
        return True
    except ImportError:
        try:
            # Adicionar diretório raiz ao path e tentar novamente
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from src.tools.mcp_nl_processor import MCPNLProcessor
            return True
        except ImportError:
            return False

# Função para extrair slug e parâmetros de uma URL do TESS
def parse_tess_url(url):
    """
    Extrai o slug do agente e parâmetros de uma URL do TESS
    
    Args:
        url: URL do TESS no formato https://tess.pareto.io/...
        
    Returns:
        Tupla (slug, parâmetros)
    """
    try:
        # Remover o @ inicial se presente
        if url.startswith('@'):
            url = url[1:]
            
        # Verificar se é uma URL válida do TESS
        if not url.startswith('https://tess.pareto.io/'):
            return None, None
            
        # Fazer o parsing da URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Extrair o slug do agente do caminho
        path_parts = parsed_url.path.split('/')
        # O slug geralmente é o último elemento do caminho
        agent_slug = path_parts[-1]
        
        # Extrair os parâmetros da query string
        query_params = urllib.parse.parse_qs(parsed_url.query)
        params = {}
        
        # Converter parâmetros de lista para valores únicos
        for key, values in query_params.items():
            if values:
                params[key] = values[0]
        
        logger.info(f"URL TESS parseada: slug={agent_slug}, params={params}")
        return agent_slug, params
    except Exception as e:
        logger.error(f"Erro ao analisar URL TESS: {e}")
        return None, None

def chat() -> None:
    """Inicia um chat com o Arcee AI usando o modo AUTO"""
    
    # Log de inicialização
    logger.info("Sistema de logging configurado. Arquivo de log: ~/.arcee/logs/arcee.log")
    
    # Verificar disponibilidade de módulos
    test_api_tess_available = is_test_api_tess_available()
    if test_api_tess_available:
        logger.info("Módulo test_api_tess disponível")
    else:
        logger.error("Módulo test_api_tess não disponível - comandos TESS não funcionarão")
    
    # Verificar disponibilidade do MCPNLProcessor
    mcp_nl_processor_available = is_mcp_nl_processor_available()
    if mcp_nl_processor_available:
        logger.info("Módulo MCPNLProcessor disponível")
    else:
        logger.info("Módulo MCPNLProcessor não disponível - comandos avançados TESS não funcionarão")
    
    logger.info("Iniciando chat com Arcee AI")
    
    # Inicializar processador de linguagem natural do TESS se disponível
    mcp_nl_processor = None
    if mcp_nl_processor_available:
        try:
            from src.tools.mcp_nl_processor import MCPNLProcessor
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
                    _mostrar_ajuda(console, test_api_tess_available)
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
                
                # Verificar comandos diretos para TESS (sem precisar de MCPNLProcessor)
                if test_api_tess_available:
                    # Comando "listar agentes"
                    if user_input.lower() in ["listar agentes", "listar os agentes", "mostrar agentes"]:
                        logger.info("Detectado comando direto: listar_agentes")
                        console.print("[italic]Executando comando: listar agentes...[/italic]")
                        
                        try:
                            # Importar a função diretamente onde é usada
                            from tests.test_api_tess import listar_agentes
                            success, data = listar_agentes(is_cli=False)
                            if success:
                                console.print("[green]✓ Comando executado com sucesso[/green]")
                                # Formatar a resposta para exibição no chat
                                tess_response = f"[bold]Agentes TESS disponíveis:[/bold]\n\n"
                                for i, agent in enumerate(data.get('data', [])[:10], 1):
                                    tipo_agente = agent.get('type', 'desconhecido')
                                    tipo_icone = "💬" if tipo_agente == "chat" else "📝" if tipo_agente == "text" else "🔄"
                                    tess_response += f"{i}. [bold]{agent.get('title', 'Sem título')}[/bold] {tipo_icone}\n"
                                    tess_response += f"   ID: {agent.get('slug', 'N/A')}\n"
                                    tess_response += f"   Tipo: {tipo_agente.capitalize()}\n"
                                    tess_response += f"   Descrição: {agent.get('description', 'Sem descrição')}\n\n"
                                tess_response += f"Total: {data.get('total', 0)} agentes disponíveis"
                                console.print(Panel(tess_response, title="Agentes TESS", border_style="green"))
                                # Adicionar à história de conversa
                                messages.append({"role": "user", "content": user_input})
                                messages.append({"role": "assistant", "content": tess_response})
                            else:
                                error_msg = data.get('error', 'Erro desconhecido')
                                console.print(f"[bold red]Erro ao listar agentes TESS:[/bold red] {error_msg}")
                        except Exception as e:
                            logger.exception(f"Erro ao executar comando listar_agentes: {e}")
                            console.print(f"[bold red]Erro ao listar agentes:[/bold red] {str(e)}")
                        
                        continue
                    
                    # Comandos para listar agentes do tipo específico
                    filtro_chat = re.match(r"listar\s+agentes\s+(tipo\s+)?(chat|conversacional|conversa)", user_input, re.IGNORECASE)
                    filtro_texto = re.match(r"listar\s+agentes\s+(tipo\s+)?(texto|text)", user_input, re.IGNORECASE)
                    
                    if filtro_chat or filtro_texto:
                        tipo_filtro = "chat" if filtro_chat else "text"
                        logger.info(f"Detectado comando direto: listar_agentes_por_tipo ({tipo_filtro})")
                        console.print(f"[italic]Executando comando: listar agentes do tipo {tipo_filtro}...[/italic]")
                        
                        try:
                            # Importar a função diretamente onde é usada
                            from tests.test_api_tess import listar_agentes
                            success, data = listar_agentes(is_cli=False, filter_type=tipo_filtro)
                            if success:
                                console.print("[green]✓ Comando executado com sucesso[/green]")
                                # Formatar a resposta para exibição no chat
                                icon = "💬" if tipo_filtro == "chat" else "📝"
                                tess_response = f"[bold]Agentes TESS do tipo {tipo_filtro.upper()} {icon}:[/bold]\n\n"
                                
                                if not data.get('data'):
                                    tess_response = f"[bold]Nenhum agente do tipo {tipo_filtro.upper()} encontrado.[/bold]"
                                else:
                                    for i, agent in enumerate(data.get('data', [])[:15], 1):
                                        tess_response += f"{i}. [bold]{agent.get('title', 'Sem título')}[/bold]\n"
                                        tess_response += f"   ID: {agent.get('slug', 'N/A')}\n"
                                        tess_response += f"   Descrição: {agent.get('description', 'Sem descrição')}\n\n"
                                    
                                    tess_response += f"Total: {len(data.get('data', []))} agentes do tipo {tipo_filtro.upper()}"
                                
                                console.print(Panel(tess_response, title=f"Agentes TESS ({tipo_filtro.upper()})", border_style="green"))
                                # Adicionar à história de conversa
                                messages.append({"role": "user", "content": user_input})
                                messages.append({"role": "assistant", "content": tess_response})
                            else:
                                error_msg = data.get('error', 'Erro desconhecido')
                                console.print(f"[bold red]Erro ao listar agentes TESS:[/bold red] {error_msg}")
                        except Exception as e:
                            logger.exception(f"Erro ao executar comando listar_agentes por tipo: {e}")
                            console.print(f"[bold red]Erro ao listar agentes por tipo:[/bold red] {str(e)}")
                        
                        continue
                    
                    # Filtro por palavra-chave
                    filtro_keyword = re.match(r"listar\s+agentes\s+(?:com\s+|que\s+contenham\s+|contendo\s+)(.+)", user_input, re.IGNORECASE)
                    if filtro_keyword:
                        keyword = filtro_keyword.group(1).strip()
                        logger.info(f"Detectado comando direto: listar_agentes_por_keyword ({keyword})")
                        console.print(f"[italic]Executando comando: listar agentes contendo '{keyword}'...[/italic]")
                        
                        try:
                            # Importar a função diretamente onde é usada
                            from tests.test_api_tess import listar_agentes
                            success, data = listar_agentes(is_cli=False, keyword=keyword)
                            if success:
                                console.print("[green]✓ Comando executado com sucesso[/green]")
                                # Formatar a resposta para exibição no chat
                                if not data.get('data'):
                                    tess_response = f"[bold]Nenhum agente encontrado contendo '{keyword}'.[/bold]"
                                else:
                                    tess_response = f"[bold]Agentes TESS contendo '{keyword}':[/bold]\n\n"
                                    for i, agent in enumerate(data.get('data', [])[:15], 1):
                                        tipo_agente = agent.get('type', 'desconhecido')
                                        tipo_icone = "💬" if tipo_agente == "chat" else "📝" if tipo_agente == "text" else "🔄"
                                        tess_response += f"{i}. [bold]{agent.get('title', 'Sem título')}[/bold] {tipo_icone}\n"
                                        tess_response += f"   ID: {agent.get('slug', 'N/A')}\n"
                                        tess_response += f"   Tipo: {tipo_agente.capitalize()}\n"
                                        tess_response += f"   Descrição: {agent.get('description', 'Sem descrição')}\n\n"
                                    
                                    tess_response += f"Total: {len(data.get('data', []))} agentes encontrados"
                                
                                console.print(Panel(tess_response, title=f"Agentes TESS (Filtro: {keyword})", border_style="green"))
                                # Adicionar à história de conversa
                                messages.append({"role": "user", "content": user_input})
                                messages.append({"role": "assistant", "content": tess_response})
                            else:
                                error_msg = data.get('error', 'Erro desconhecido')
                                console.print(f"[bold red]Erro ao listar agentes TESS:[/bold red] {error_msg}")
                        except Exception as e:
                            logger.exception(f"Erro ao executar comando listar_agentes por keyword: {e}")
                            console.print(f"[bold red]Erro ao listar agentes por palavra-chave:[/bold red] {str(e)}")
                        
                        continue
                    
                    # Detectar e executar URL do TESS
                    if user_input.startswith("@https://tess.pareto.io/") or user_input.startswith("https://tess.pareto.io/"):
                        logger.info("Detectada URL do TESS")
                        console.print("[italic]Detectada URL do TESS. Tentando executar agente...[/italic]")
                        
                        # Extrair slug e parâmetros
                        agent_slug, params = parse_tess_url(user_input)
                        
                        if not agent_slug:
                            console.print("[bold red]Erro:[/bold red] Não foi possível extrair o ID do agente da URL")
                            continue
                            
                        # Preparar mensagem (vazia por padrão, pois é esperado que o usuário forneça uma logo depois)
                        console.print(f"[bold]Agente TESS identificado:[/bold] {agent_slug}")
                        console.print("[italic]Por favor, digite sua mensagem para o agente:[/italic]")
                        
                        # Solicitar a mensagem do usuário
                        agent_message = Prompt.ask("\n[bold green]Mensagem para o agente[/bold green]")
                        
                        if not agent_message.strip():
                            console.print("[yellow]⚠ Mensagem vazia. Operação cancelada.[/yellow]")
                            continue
                            
                        logger.info(f"Executando agente TESS via URL: {agent_slug}")
                        console.print(f"[italic]Executando agente TESS {agent_slug}...[/italic]")
                        
                        try:
                            # Importar a função diretamente onde é usada
                            from tests.test_api_tess import executar_agente
                            
                            # Preparar parâmetros específicos da URL
                            specific_params = None
                            if params:
                                specific_params = {
                                    "message": agent_message
                                }
                                # Adicionar outros parâmetros da URL
                                for key, value in params.items():
                                    if key not in ["_chat_id"]:  # Ignorar parâmetros específicos da interface
                                        specific_params[key] = value
                                
                                logger.info(f"Usando parâmetros específicos da URL: {specific_params}")
                            
                            # Executar o agente
                            if specific_params:
                                success, data = executar_agente(agent_slug, agent_message, is_cli=False, specific_params=specific_params)
                            else:
                                success, data = executar_agente(agent_slug, agent_message, is_cli=False)
                                
                            if success and "output" in data:
                                console.print("[green]✓ Agente TESS executado com sucesso[/green]")
                                output_text = data["output"]
                                console.print(Panel(output_text, title=f"Resposta do Agente: {agent_slug}", border_style="green"))
                                # Adicionar à história de conversa
                                messages.append({"role": "user", "content": f"URL: {user_input}\nMensagem: {agent_message}"})
                                messages.append({"role": "assistant", "content": output_text})
                            elif success and "full_response" in data and "output" in data["full_response"]:
                                console.print("[green]✓ Agente TESS executado com sucesso[/green]")
                                output_text = data["full_response"]["output"]
                                console.print(Panel(output_text, title=f"Resposta do Agente: {agent_slug}", border_style="green"))
                                # Adicionar à história de conversa
                                messages.append({"role": "user", "content": f"URL: {user_input}\nMensagem: {agent_message}"})
                                messages.append({"role": "assistant", "content": output_text})
                            else:
                                error_msg = data.get('error', 'Erro desconhecido')
                                console.print(f"[bold red]Erro ao executar agente TESS:[/bold red] {error_msg}")
                                
                                # Tentar extrair detalhes adicionais do erro
                                if 'details' in data:
                                    details = data['details']
                                    if isinstance(details, dict) and 'text' in details:
                                        try:
                                            error_json = json.loads(details['text'])
                                            if 'message' in error_json:
                                                console.print(f"[bold red]Detalhes:[/bold red] {error_json['message']}")
                                        except:
                                            pass
                        except Exception as e:
                            logger.exception(f"Erro ao executar agente via URL: {e}")
                            console.print(f"[bold red]Erro ao executar agente:[/bold red] {str(e)}")
                        
                        continue
                    
                    # Comando simplificado "executar [agent_id] [mensagem]" (formato direto sem o formato agente/mensagem)
                    comando_executar_simples = re.match(r"executar\s+([a-zA-Z0-9_-]+)\s+\"(.+)\"", user_input, re.IGNORECASE)
                    if comando_executar_simples:
                        agent_id = comando_executar_simples.group(1)
                        mensagem = comando_executar_simples.group(2)
                        
                        if not mensagem:
                            console.print("[yellow]⚠ É necessário fornecer uma mensagem para o agente.[/yellow]")
                            console.print("[italic]Exemplo: executar professional-dev-ai \"Como criar uma classe singleton em Python?\"[/italic]")
                            continue
                        
                        logger.info(f"Detectado comando direto simplificado: executar {agent_id}")
                        console.print(f"[italic]Executando agente TESS {agent_id}...[/italic]")
                        
                        try:
                            # Importar a função diretamente onde é usada
                            from tests.test_api_tess import executar_agente
                            success, data = executar_agente(agent_id, mensagem, is_cli=False)
                            if success and "output" in data:
                                console.print("[green]✓ Agente TESS executado com sucesso[/green]")
                                output_text = data["output"]
                                console.print(Panel(output_text, title=f"Resposta do Agente: {agent_id}", border_style="green"))
                                # Adicionar à história de conversa
                                messages.append({"role": "user", "content": user_input})
                                messages.append({"role": "assistant", "content": output_text})
                            elif success and "full_response" in data and "output" in data["full_response"]:
                                console.print("[green]✓ Agente TESS executado com sucesso[/green]")
                                output_text = data["full_response"]["output"]
                                console.print(Panel(output_text, title=f"Resposta do Agente: {agent_id}", border_style="green"))
                                # Adicionar à história de conversa
                                messages.append({"role": "user", "content": user_input})
                                messages.append({"role": "assistant", "content": output_text})
                            else:
                                error_msg = data.get('error', 'Erro desconhecido')
                                console.print(f"[bold red]Erro ao executar agente TESS:[/bold red] {error_msg}")
                                
                                # Tentar extrair detalhes adicionais do erro se disponível
                                if 'details' in data:
                                    details = data['details']
                                    if isinstance(details, dict) and 'text' in details:
                                        try:
                                            error_json = json.loads(details['text'])
                                            if 'message' in error_json:
                                                console.print(f"[bold red]Detalhes:[/bold red] {error_json['message']}")
                                        except:
                                            pass
                        except Exception as e:
                            logger.exception(f"Erro ao executar comando executar_agente: {e}")
                            console.print(f"[bold red]Erro ao executar agente:[/bold red] {str(e)}")
                        
                        continue
                    
                    # Comando "executar agente"
                    comando_executar = re.match(r"executar\s+agente\s+([a-zA-Z0-9_-]+)(?:\s+com\s+mensagem\s+(.+))?", user_input, re.IGNORECASE)
                    if comando_executar:
                        agent_id = comando_executar.group(1)
                        mensagem = comando_executar.group(2) if comando_executar.group(2) else ""
                        
                        if not mensagem:
                            console.print("[yellow]⚠ É necessário fornecer uma mensagem para o agente.[/yellow]")
                            console.print("[italic]Exemplo: executar agente professional-dev-ai com mensagem \"Qual a melhor forma de implementar um singleton em Python?\"[/italic]")
                            continue
                        
                        logger.info(f"Detectado comando direto: executar_agente {agent_id}")
                        console.print(f"[italic]Executando agente TESS {agent_id}...[/italic]")
                        
                        try:
                            # Importar a função diretamente onde é usada
                            from tests.test_api_tess import executar_agente
                            success, data = executar_agente(agent_id, mensagem, is_cli=False)
                            if success and "output" in data:
                                console.print("[green]✓ Agente TESS executado com sucesso[/green]")
                                output_text = data["output"]
                                console.print(Panel(output_text, title=f"Resposta do Agente: {agent_id}", border_style="green"))
                                # Adicionar à história de conversa
                                messages.append({"role": "user", "content": user_input})
                                messages.append({"role": "assistant", "content": output_text})
                            elif success and "full_response" in data and "output" in data["full_response"]:
                                console.print("[green]✓ Agente TESS executado com sucesso[/green]")
                                output_text = data["full_response"]["output"]
                                console.print(Panel(output_text, title=f"Resposta do Agente: {agent_id}", border_style="green"))
                                # Adicionar à história de conversa
                                messages.append({"role": "user", "content": user_input})
                                messages.append({"role": "assistant", "content": output_text})
                            else:
                                error_msg = data.get('error', 'Erro desconhecido')
                                console.print(f"[bold red]Erro ao executar agente TESS:[/bold red] {error_msg}")
                                
                                # Tentar extrair detalhes adicionais do erro se disponível
                                if 'details' in data:
                                    details = data['details']
                                    if isinstance(details, dict) and 'text' in details:
                                        try:
                                            error_json = json.loads(details['text'])
                                            if 'message' in error_json:
                                                console.print(f"[bold red]Detalhes:[/bold red] {error_json['message']}")
                                        except:
                                            pass
                        except Exception as e:
                            logger.exception(f"Erro ao executar comando executar_agente: {e}")
                            console.print(f"[bold red]Erro ao executar agente:[/bold red] {str(e)}")
                        
                        continue
                
                # Verificar comandos TESS via test_api_tess
                tess_response = None
                if test_api_tess_available and user_input.startswith("test_api_tess"):
                    try:
                        from tests.test_api_tess import listar_agentes, executar_agente
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
                    except Exception as e:
                        logger.exception(f"Erro ao processar comando test_api_tess: {e}")
                        tess_response = f"[bold red]Erro ao processar comando test_api_tess:[/bold red] {str(e)}"
                
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
                            # Implementar comando listar_agentes via MCPNLProcessor
                            if tipo_comando == "listar_agentes":
                                logger.info("Processando comando listar_agentes")
                                try:
                                    from tests.test_api_tess import listar_agentes
                                    success, data = listar_agentes(is_cli=False)
                                    if success:
                                        console.print(f"\n[bold green]Assistente:[/bold green]")
                                        # Formatar a resposta para exibição no chat
                                        tess_response = f"[bold]Agentes TESS disponíveis:[/bold]\n\n"
                                        for i, agent in enumerate(data.get('data', [])[:20], 1):
                                            tipo_agente = agent.get('type', 'desconhecido')
                                            tipo_icone = "💬" if tipo_agente == "chat" else "📝" if tipo_agente == "text" else "🔄"
                                            tess_response += f"{i}. [bold]{agent.get('title', 'Sem título')}[/bold] {tipo_icone}\n"
                                            tess_response += f"   ID: {agent.get('slug', 'N/A')}\n"
                                            tess_response += f"   Tipo: {tipo_agente.capitalize()}\n"
                                            tess_response += f"   Descrição: {agent.get('description', 'Sem descrição')}\n\n"
                                        tess_response += f"Total: {data.get('total', 0)} agentes disponíveis"
                                        console.print(Panel(tess_response, title="Agentes TESS", border_style="green"))
                                        # Adicionar à história de conversa
                                        messages.append({"role": "user", "content": user_input})
                                        messages.append({"role": "assistant", "content": tess_response})
                                    else:
                                        console.print(f"[bold red]Erro ao listar agentes TESS:[/bold red] {data.get('error', 'Erro desconhecido')}")
                                except Exception as e:
                                    logger.exception(f"Erro ao listar agentes via MCPNLProcessor: {e}")
                                    console.print(f"[bold red]Erro ao listar agentes:[/bold red] {str(e)}")
                                continue
                            
                            # Implementar comando executar_agente via MCPNLProcessor
                            elif tipo_comando == "executar_agente":
                                logger.info("Processando comando executar_agente")
                                try:
                                    from tests.test_api_tess import executar_agente
                                    agent_id = params.get("agent_id", "")
                                    mensagem = params.get("mensagem", "")
                                    if not agent_id:
                                        console.print("[bold red]Erro:[/bold red] ID do agente não especificado. Use o formato: executar agente <id> com mensagem <texto>")
                                        continue
                                    if not mensagem:
                                        console.print("[bold red]Erro:[/bold red] Mensagem não especificada. Use o formato: executar agente <id> com mensagem <texto>")
                                        continue
                                    
                                    console.print(f"[italic]Executando agente TESS: {agent_id}...[/italic]")
                                    success, data = executar_agente(agent_id, mensagem, is_cli=False)
                                    if success:
                                        console.print(f"\n[bold green]Assistente:[/bold green]")
                                        if "output" in data:
                                            output = data["output"]
                                            console.print(Panel(output, title=f"Resposta do Agente: {agent_id}", border_style="green"))
                                            # Adicionar à história de conversa
                                            messages.append({"role": "user", "content": user_input})
                                            messages.append({"role": "assistant", "content": output})
                                        # Verificar se a resposta está na estrutura full_response
                                        elif "full_response" in data and isinstance(data["full_response"], dict):
                                            output = data["full_response"].get("output", "Sem resposta")
                                            console.print(Panel(output, title=f"Resposta do Agente: {agent_id}", border_style="green"))
                                            # Adicionar à história de conversa
                                            messages.append({"role": "user", "content": user_input})
                                            messages.append({"role": "assistant", "content": output})
                                        else:
                                            # Se não encontrar output, mostrar resposta genérica
                                            console.print(Panel(str(data), title=f"Resposta do Agente: {agent_id}", border_style="green"))
                                            messages.append({"role": "user", "content": user_input})
                                            messages.append({"role": "assistant", "content": str(data)})
                                    else:
                                        error_msg = data.get('error', 'Erro desconhecido')
                                        console.print(f"[bold red]Erro ao executar agente TESS:[/bold red] {error_msg}")
                                        
                                        # Tentar extrair detalhes adicionais do erro se disponível
                                        if 'details' in data:
                                            details = data['details']
                                            if isinstance(details, dict) and 'text' in details:
                                                try:
                                                    error_json = json.loads(details['text'])
                                                    if 'message' in error_json:
                                                        console.print(f"[bold red]Detalhes:[/bold red] {error_json['message']}")
                                                except:
                                                    pass
                                except Exception as e:
                                    logger.exception(f"Erro ao executar agente via MCPNLProcessor: {e}")
                                    console.print(f"[bold red]Erro ao executar agente:[/bold red] {str(e)}")
                                continue
                            
                            # Outros comandos do processador
                            else:
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

def _mostrar_ajuda(console, test_api_tess_available):
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
    
    # Comandos TESS diretos
    if test_api_tess_available:
        console.print("\n[bold]Comandos TESS:[/bold]")
        console.print("• [bold]listar agentes[/bold] - Lista agentes TESS disponíveis")
        console.print("• [bold]listar agentes tipo chat[/bold] - Lista apenas agentes de chat")
        console.print("• [bold]listar agentes tipo texto[/bold] - Lista apenas agentes de texto")
        console.print("• [bold]listar agentes contendo <palavra-chave>[/bold] - Lista agentes com palavra-chave")
        console.print("• [bold]executar <id> \"<texto>\"[/bold] - Executa um agente TESS (formato simplificado)")
        console.print("  [dim]Exemplo: executar professional-dev-ai \"Como implementar um singleton em Python?\"[/dim]")
        console.print("• [bold]executar agente <id> com mensagem \"<texto>\"[/bold] - Executa um agente TESS (formato completo)")
        console.print("  [dim]Exemplo: executar agente professional-dev-ai com mensagem \"Como implementar um singleton em Python?\"[/dim]")
        console.print("• [bold]@https://tess.pareto.io/... (URL)[/bold] - Executar agente diretamente da URL do TESS")
        console.print("  [dim]Exemplo: @https://tess.pareto.io/pt-BR/dashboard/user/ai/chat/ai-chat/professional-dev-ai[/dim]")
    
    # Comandos TESS API (legado)
    if test_api_tess_available:
        console.print("\n[bold]Comandos TESS API (legado):[/bold]")
        console.print("• [bold]test_api_tess listar[/bold] - Lista agentes TESS disponíveis")
        console.print("• [bold]test_api_tess executar <id> <mensagem>[/bold] - Executa um agente TESS específico")
    
    # Comandos específicos do Arcee
    console.print("\n[bold]Dicas de uso:[/bold]")
    console.print("• Para tarefas criativas, use frases como 'criar', 'escrever' ou 'imaginar'")
    console.print("• Para consultas técnicas, seja específico sobre tecnologias")
   
if __name__ == "__main__":
    chat() 