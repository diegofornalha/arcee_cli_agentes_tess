#!/bin/bash

# Script de teste para a API TESS via MCP

echo "=== Testando API TESS via MCP ==="

# Carrega variáveis de ambiente
if [ -f ../.env ]; then
  source ../.env
  echo "Variáveis de ambiente carregadas do arquivo ../.env"
else
  echo "Arquivo .env não encontrado. Usando valores padrão."
fi

# Verifica a sessão MCP
if [ -z "$MCP_SESSION_ID" ]; then
  echo "❌ Erro: MCP_SESSION_ID não definido"
  echo "Execute 'npx mcpx login' para obter uma sessão"
  exit 1
else
  echo "MCP Session ID: $MCP_SESSION_ID"
fi

# Verifica a API key da TESS
if [ -z "$TESS_API_KEY" ]; then
  echo "❌ Erro: TESS_API_KEY não definido"
  echo "Adicione TESS_API_KEY ao arquivo .env"
  exit 1
fi

# Testa listagem de agentes
echo -e "\nListando agentes TESS..."
npx mcpx run mcp-server-agno.listar_agentes_tess --json '{"page": 1, "per_page": 5}' --session "$MCP_SESSION_ID" 

# Testa listagem de arquivos
echo -e "\nListando arquivos TESS..."
npx mcpx run mcp-server-agno.listar_arquivos_tess --json '{"page": 1, "per_page": 5}' --session "$MCP_SESSION_ID"

echo -e "\n✅ Teste concluído" 