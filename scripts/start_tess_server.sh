#!/bin/bash

# Script para iniciar o servidor TESS MCP

# Código de cores para saída
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Encontra o diretório raiz do projeto
get_project_root() {
    # Obtém o caminho do diretório atual do script
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    # Navega um nível acima para chegar ao diretório raiz do projeto
    echo "$(cd "$script_dir/.." && pwd)"
}

PROJECT_ROOT=$(get_project_root)
# Corrigindo o caminho para o diretório correto do servidor
SERVIDOR_DIR="$PROJECT_ROOT/mcp-server-agno-xtp"

echo -e "${YELLOW}=== Iniciando Servidor TESS MCP ===${NC}"

# Verifica se o diretório do servidor existe
if [ ! -d "$SERVIDOR_DIR" ]; then
    echo -e "${RED}❌ Erro: Diretório do servidor MCP-TESS não encontrado${NC}"
    echo "Caminho buscado: $SERVIDOR_DIR"
    exit 1
fi

# Navega para o diretório do servidor
cd "$SERVIDOR_DIR" || exit 1

# Cria o diretório "build" se não existir
if [ ! -d "build" ]; then
    echo -e "${YELLOW}Criando diretório build...${NC}"
    mkdir -p build
fi

# Verifica se o arquivo index.js existe na pasta build
if [ ! -f "build/index.js" ]; then
    echo -e "${YELLOW}Compilando servidor...${NC}"
    # Verifica se tem o npm instalado
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ Erro: npm não encontrado. Por favor, instale o Node.js e npm.${NC}"
        exit 1
    fi
    
    # Instala dependências e compila
    npm install && npm run build
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro ao compilar o servidor.${NC}"
        exit 1
    fi
fi

# Inicia o servidor
echo -e "${GREEN}Iniciando servidor...${NC}"
node build/index.js 