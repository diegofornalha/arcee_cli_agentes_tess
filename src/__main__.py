#!/usr/bin/env python
"""
CLI principal para interação com a API TESS através do MCP.
"""

import sys
import os
import logging
import click
from typing import Optional
from dotenv import load_dotenv
from .utils.logging import configure_logging
from .commands.mcp import main_configurar, main_listar, main_executar

# Importar o chat Arcee usando caminho absoluto em vez de relativo
from crew.arcee_chat import chat as arcee_chat

# Configurar logging
configure_logging()
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

@click.group()
def cli():
    """CLI para interação com a API TESS através do MCP."""
    logger.info("CLI TESS iniciada")
    pass

@cli.command("chat")
def chat():
    """Inicia um chat interativo com o Arcee AI usando modo AUTO."""
    arcee_chat()

# Adicionar alias para facilitar o uso
@cli.command("conversar")
def conversar():
    """Alias para o comando 'chat'."""
    arcee_chat()

# Cria um grupo de comandos para o MCP
@cli.group("mcp")
def mcp_group():
    """Comandos para gerenciar as integrações com MCP.run."""
    pass

@mcp_group.command("configurar")
@click.option("--session-id", help="ID de sessão MCP.run existente")
def mcp_configurar(session_id: Optional[str] = None):
    """Configura a integração com MCP.run."""
    main_configurar(session_id)

@mcp_group.command("listar")
def mcp_listar():
    """Lista todas as ferramentas disponíveis no MCP.run."""
    main_listar()

@mcp_group.command("executar")
@click.argument("nome", required=True)
@click.option("--params", help="Parâmetros da ferramenta em formato JSON")
def mcp_executar(nome: str, params: Optional[str] = None):
    """Executa uma ferramenta MCP.run específica."""
    main_executar(nome, params)

if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        logger.error(f"Erro ao executar comando: {str(e)}")
        sys.exit(1) 