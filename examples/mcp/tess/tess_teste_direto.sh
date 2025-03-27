#!/bin/bash

# Script para testar a API TESS diretamente (sem MCP)

echo "=== Testando API TESS Diretamente ==="

# Carrega variáveis de ambiente
if [ -f ../.env ]; then
  source ../.env
  echo "Variáveis de ambiente carregadas do arquivo ../.env"
else
  echo "Arquivo .env não encontrado. Usando valores padrão."
fi

# Verifica a API key da TESS
if [ -z "$TESS_API_KEY" ]; then
  echo "❌ Erro: TESS_API_KEY não definido"
  echo "Adicione TESS_API_KEY ao arquivo .env"
  exit 1
else
  echo "API Key: ${TESS_API_KEY:0:5}...${TESS_API_KEY: -5}"
fi

# URL base da API TESS
API_URL="https://tess.pareto.io/api"

# Configurações para curl
HEADERS=(
  -H "Authorization: Bearer $TESS_API_KEY"
  -H "Content-Type: application/json"
)

# Testa listagem de agentes
echo -e "\nListando agentes TESS..."
curl "${HEADERS[@]}" -s "$API_URL/agents?page=1&per_page=5" | jq '.'

# Testa listagem de arquivos
echo -e "\nListando arquivos TESS..."
curl "${HEADERS[@]}" -s "$API_URL/files?page=1&per_page=5" | jq '.'

echo -e "\n✅ Teste concluído" 