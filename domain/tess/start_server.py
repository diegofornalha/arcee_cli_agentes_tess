#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para iniciar o servidor TESS MCP.

Este script inicia o servidor TESS MCP (Task and Event Simple System)
independentemente do resto da aplicação.
"""

import os
import sys
import logging

# Verificar dependências
try:
    from flask import Flask
    from flask_cors import CORS
except ImportError:
    print("Flask ou Flask-CORS não estão instalados. Execute:")
    print("pip install flask flask-cors")
    sys.exit(1)

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importa a aplicação Flask do módulo server
from domain.agno.server import app

def main():
    """Função principal para iniciar o servidor"""
    host = os.environ.get("TESS_HOST", "127.0.0.1")
    port = int(os.environ.get("TESS_PORT", 5000))
    debug = os.environ.get("TESS_DEBUG", "").lower() in ("true", "1", "t")
    
    logger.info(f"Iniciando servidor TESS em {host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main() 