#!/usr/bin/env python
"""
Chat com Arcee AI usando o modo AUTO.
"""

import sys
import logging
from ..utils.logging import get_logger, configure_logging
from crew.arcee_chat import chat as arcee_chat

# Configurar logging
configure_logging()
logger = get_logger(__name__)

def main():
    """Função principal que inicia o chat com Arcee AI."""
    try:
        # Executa o chat Arcee com modo AUTO
        arcee_chat()
    except Exception as e:
        logger.exception(f"Erro durante execução do chat: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 