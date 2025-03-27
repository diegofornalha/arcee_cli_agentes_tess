#!/usr/bin/env python
"""
Script de teste para o CLI integrado com a API TESS.
"""

import subprocess
import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def main():
    """Função principal que testa o CLI."""
    # Verificar se as variáveis de ambiente necessárias estão configuradas
    if not os.getenv("TESS_API_KEY"):
        print("Erro: TESS_API_KEY não configurada. Configure no arquivo .env")
        sys.exit(1)
    
    print("\n=== Testando listagem de agentes ===")
    subprocess.run(["python", "-m", "arcee_cli", "tess", "listar-agentes"], check=False)
    
    # Verificar se recebemos o ID do agente como argumento
    if len(sys.argv) < 2:
        print("\nPara testar o chat, use: python test_tess_cli.py <agent_id>")
        sys.exit(0)
    
    agent_id = sys.argv[1]
    print(f"\n=== Testando detalhes do agente {agent_id} ===")
    subprocess.run(["python", "-m", "arcee_cli", "tess", "detalhes-agente", agent_id], check=False)
    
    print(f"\n=== Testando chat com o agente {agent_id} ===")
    subprocess.run(["python", "-m", "arcee_cli", "tess-chat", agent_id], check=False)

if __name__ == "__main__":
    main() 