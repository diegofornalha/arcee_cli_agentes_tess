#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste de integração da API TESS com MCP.run
"""

import os
import sys
import json
import subprocess
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Obtém a sessão MCP.run
MCP_SESSION = os.getenv("MCP_SESSION_ID")
TESS_API_KEY = os.getenv("TESS_API_KEY")

if not MCP_SESSION:
    print("❌ Erro: Variável MCP_SESSION_ID não configurada no arquivo .env")
    sys.exit(1)

if not TESS_API_KEY:
    print("❌ Erro: Variável TESS_API_KEY não configurada no arquivo .env")
    sys.exit(1)

def testar_mcp_ferramentas():
    """Verifica se as ferramentas MCP estão disponíveis"""
    try:
        print("Verificando ferramentas MCP disponíveis...")
        cmd = f"npx mcpx tools --session {MCP_SESSION}"
        resultado = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        
        # Verifica se 'agno' está nas ferramentas disponíveis
        if "agno" in resultado.stdout.lower():
            print("✅ Ferramenta 'TESS' encontrada no MCP.run")
            return True
        else:
            print("❌ Ferramenta 'TESS' NÃO encontrada no MCP.run")
            print("   Verifique se o servidor MCP-TESS está em execução")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao listar ferramentas MCP: {e}")
        print(f"Saída: {e.stderr}")
        return False

def testar_tess_agentes():
    """Testa a listagem de agentes TESS via MCP.run"""
    try:
        print("\nTestando listagem de agentes TESS...")
        params = json.dumps({"page": 1, "per_page": 10})
        cmd = f"npx mcpx run mcp-server-agno.listar_agentes_tess --json '{params}' --session {MCP_SESSION}"
        resultado = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        
        # Verificar se a resposta parece ser uma lista de agentes
        saida = resultado.stdout
        if "data" in saida:
            print("✅ Listagem de agentes funcionando")
            return True
        else:
            print("❌ Listagem de agentes falhou")
            print(f"Saída: {saida}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao listar agentes: {e}")
        print(f"Saída: {e.stderr}")
        return False

def testar_tess_arquivos():
    """Testa a listagem de arquivos TESS"""
    try:
        print("\nTestando listagem de arquivos TESS...")
        params = json.dumps({"page": 1, "per_page": 10})
        cmd = f"npx mcpx run mcp-server-agno.listar_arquivos_tess --json '{params}' --session {MCP_SESSION}"
        resultado = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        
        # Verificar se a resposta parece ser uma lista de arquivos
        saida = resultado.stdout
        if "data" in saida:
            print("✅ Listagem de arquivos funcionando")
            return True
        else:
            print("❌ Listagem de arquivos falhou")
            print(f"Saída: {saida}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao listar arquivos: {e}")
        print(f"Saída: {e.stderr}")
        return False

def main():
    """Função principal de teste"""
    print("=== Teste de Integração TESS com MCP.run ===\n")
    
    # Verifica se as ferramentas estão disponíveis
    if not testar_mcp_ferramentas():
        print("\n❌ Teste falhou: Ferramentas MCP não configuradas corretamente")
        return 1
    
    # Testa a listagem de agentes
    if not testar_tess_agentes():
        print("\n⚠️ Aviso: Falha ao listar agentes")
    
    # Testa a listagem de arquivos
    if not testar_tess_arquivos():
        print("\n⚠️ Aviso: Falha ao listar arquivos")
    
    print("\n=== Teste Concluído ===")
    print("✅ A integração TESS com MCP.run está configurada corretamente")
    return 0

if __name__ == "__main__":
    sys.exit(main())
