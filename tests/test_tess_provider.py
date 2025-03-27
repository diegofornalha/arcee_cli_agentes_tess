#!/usr/bin/env python
"""
Script de teste para o provedor TESS.
"""

import os
import sys
from dotenv import load_dotenv
from arcee_cli.src.providers.tess_provider import TessProvider
from rich import print

# Carregar variáveis de ambiente
load_dotenv()

def main():
    """Teste do provedor da API TESS."""
    try:
        # Inicializar provedor TESS
        provider = TessProvider()
        
        # Testar conexão
        status, message = provider.health_check()
        if status:
            print("[green]✅ Conexão com TESS estabelecida[/green]")
        else:
            print(f"[red]❌ Erro na conexão: {message}[/red]")
            return
            
        # Listar agentes
        print("\n[blue]📋 Listando agentes TESS:[/blue]")
        agents = provider.list_agents()
        if not agents:
            print("[yellow]Nenhum agente encontrado[/yellow]")
            return
            
        for agent in agents:
            print(f"- {agent.get('name', 'N/A')} (ID: {agent.get('id', 'N/A')})")
        
        # Obter detalhes do primeiro agente
        if agents:
            print("\n[blue]🔍 Detalhes do primeiro agente:[/blue]")
            first_agent_id = str(agents[0].get('id', ''))
            if first_agent_id:
                agent_details = provider.get_agent(first_agent_id)
                if agent_details:
                    print("Nome:", agent_details.get('name', 'N/A'))
                    print("ID:", agent_details.get('id', 'N/A'))
                    print("Descrição:", agent_details.get('description', 'N/A'))
                else:
                    print("[yellow]Não foi possível obter detalhes do agente[/yellow]")
            else:
                print("[yellow]ID do agente não encontrado[/yellow]")
            
    except Exception as e:
        print(f"[red]❌ Erro: {str(e)}[/red]")

if __name__ == "__main__":
    main() 