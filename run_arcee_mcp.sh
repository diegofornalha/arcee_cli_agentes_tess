#!/bin/bash

# Ativar o ambiente virtual
source venv/bin/activate

# Verificar se há argumentos
if [ $# -eq 0 ]; then
    # Sem argumentos, executar com a pergunta padrão
    python arcee_agno_mcp.py
else
    # Passar todos os argumentos para o script
    python arcee_agno_mcp.py "$@"
fi 