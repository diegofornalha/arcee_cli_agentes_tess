"""
Utilitários de configuração de logging para o CLI Arcee.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# Diretório para armazenar logs
LOG_DIR = os.path.expanduser("~/.arcee_cli/logs")
LOG_FILE = os.path.join(LOG_DIR, "arcee_cli.log")

def get_logger(name):
    """Retorna um logger configurado para o módulo especificado."""
    return logging.getLogger(name)

def configure_logging(level=logging.INFO):
    """Configura o sistema de logging global."""
    # Criar diretório de logs se não existir
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Formato do log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configuração básica
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Log para arquivo com rotação
            RotatingFileHandler(
                LOG_FILE,
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3
            ),
            # Log para console
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduzir o nível de log de bibliotecas muito verbosas
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    # Log inicial
    logging.getLogger(__name__).debug("Sistema de logging configurado") 