#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Iniciando setup do servidor TESS com MCP...${NC}"

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js não encontrado. Por favor, instale o Node.js 18+${NC}"
    exit 1
fi

# Verificar Rust
if ! command -v rustc &> /dev/null; then
    echo -e "${RED}Rust não encontrado. Por favor, instale o Rust${NC}"
    exit 1
fi

# Adicionar target wasm32-wasip1
echo -e "${YELLOW}Adicionando target wasm32-wasip1...${NC}"
rustup target add wasm32-wasip1

# Instalar dependências Node.js
echo -e "${YELLOW}Instalando dependências Node.js...${NC}"
npm install

# Compilar plugin WebAssembly
echo -e "${YELLOW}Compilando plugin WebAssembly...${NC}"
npm run build

# Verificar arquivo .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}Criando arquivo .env...${NC}"
    cp .env.example .env
    echo -e "${GREEN}Arquivo .env criado. Por favor, configure suas variáveis de ambiente.${NC}"
fi

echo -e "${GREEN}Setup concluído!${NC}"
echo -e "Para iniciar o servidor:"
echo -e "  ${YELLOW}npm start${NC}     # Produção"
echo -e "  ${YELLOW}npm run dev${NC}   # Desenvolvimento com hot-reload" 