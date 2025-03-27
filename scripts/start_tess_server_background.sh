#!/bin/bash

# Script para iniciar o servidor MCP-TESS em segundo plano

# Define API key como parâmetro opcional
API_KEY="$1"

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Iniciando Servidor MCP-TESS em segundo plano ===${NC}"

# Determina o diretório raiz do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# Corrigindo o caminho para o diretório correto do servidor
SERVIDOR_DIR="$PROJECT_ROOT/mcp-server-tess-xtp"

# Verifica se o servidor já está rodando
if pgrep -f "node.*server.js" > /dev/null; then
    echo -e "${GREEN}✅ Servidor MCP-TESS já está rodando!${NC}"
    exit 0
fi

# Vai para o diretório do servidor
if [ ! -d "$SERVIDOR_DIR" ]; then
    echo -e "${RED}❌ Erro: Diretório do servidor MCP-TESS não encontrado${NC}"
    echo "Caminho buscado: $SERVIDOR_DIR"
    exit 1
fi

# Cria diretório de logs se não existir
mkdir -p "$SERVIDOR_DIR/logs"

# Informa sobre a API Key
if [ -n "$API_KEY" ]; then
    echo -e "Usando API Key personalizada: ${GREEN}[...]${NC}"
else
    echo "Usando API Key do arquivo .env"
fi

# Inicia o servidor em segundo plano
echo "Iniciando o servidor em segundo plano..."
# Se API Key foi fornecida, sobrescreve a variável de ambiente
if [ -n "$API_KEY" ]; then
    (cd "$SERVIDOR_DIR" && TESS_API_KEY="$API_KEY" node server.js > logs/tess-server.log 2>&1 &)
else
    (cd "$SERVIDOR_DIR" && node server.js > logs/tess-server.log 2>&1 &)
fi

# Aguarda um pouco para verificar se iniciou corretamente
sleep 2

# Verifica se o servidor está rodando
if pgrep -f "node.*server.js" > /dev/null; then
    echo -e "${GREEN}✅ Servidor MCP-TESS iniciado com sucesso em segundo plano!${NC}"
    echo "Log disponível em: $SERVIDOR_DIR/logs/tess-server.log"
    
    # Mostrar o PID para referência
    PID=$(pgrep -f "node.*server.js")
    echo -e "PID: ${GREEN}$PID${NC}"
    echo "Para encerrar o servidor: kill $PID"
else
    echo -e "${RED}❌ Falha ao iniciar o servidor em segundo plano${NC}"
    echo "Verifique o log para mais detalhes: $SERVIDOR_DIR/logs/tess-server.log"
    exit 1
fi 