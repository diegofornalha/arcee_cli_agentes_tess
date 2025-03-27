#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLI para o servidor TESS MCP.

Este módulo fornece uma interface de linha de comando para iniciar e gerenciar
o servidor TESS MCP (Task and Event Simple System).
"""

import os
import sys
import argparse
import logging

from arcee_cli.domain.tess.server import run_server

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Processa os argumentos da linha de comando"""
    parser = argparse.ArgumentParser(description='Servidor TESS MCP (Task and Event Simple System)')
    parser.add_argument('--host', default='0.0.0.0', help='Host para escutar (padrão: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Porta para escutar (padrão: 5000)')
    parser.add_argument('--debug', action='store_true', help='Executa em modo de depuração')
    parser.add_argument('--data-dir', default=os.path.expanduser('~/.tess'),
                        help='Diretório para armazenar os dados (padrão: ~/.tess)')
    parser.add_argument('--api-key', help='Chave de API para autenticação (opcional)')
    
    return parser.parse_args()

def main():
    """Função principal do CLI"""
    args = parse_args()
    
    # Configura as variáveis de ambiente
    os.environ['TESS_DATA_DIR'] = args.data_dir
    if args.api_key:
        os.environ['TESS_API_KEY'] = args.api_key
    
    # Exibe informações de inicialização
    logger.info(f"Iniciando servidor TESS MCP em {args.host}:{args.port}")
    logger.info(f"Diretório de dados: {args.data_dir}")
    if args.api_key:
        logger.info("Autenticação com API key ativada")
    if args.debug:
        logger.info("Modo de depuração ativado")
    
    # Inicia o servidor
    try:
        run_server(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        logger.info("Servidor encerrado pelo usuário")
    except Exception as e:
        logger.exception(f"Erro ao iniciar servidor: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 