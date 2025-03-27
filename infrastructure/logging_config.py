#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuração de logging para a CLI Arcee
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler
import sys

# Configuração de diretórios
HOME_DIR = os.path.expanduser("~")
ARCEE_DIR = os.path.join(HOME_DIR, ".arcee")
LOG_DIR = os.path.join(ARCEE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "arcee.log")

# Garantir que os diretórios existam
def ensure_directories_exist():
    """Garante que os diretórios necessários existam."""
    os.makedirs(LOG_DIR, exist_ok=True)

def configure_logging(level=logging.INFO):
    """Configura o sistema de logging.
    
    Args:
        level: Nível de logging (padrão: logging.INFO)
    """
    ensure_directories_exist()
    
    # Configurar formato de log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configurar manipulador de console
    console_handler = RichHandler(rich_tracebacks=True)
    console_handler.setLevel(level)
    
    # Configurar manipulador de arquivo
    file_handler = RotatingFileHandler(
        LOG_FILE, 
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Configurar logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Configurar loggers específicos de bibliotecas
    configurar_loggers_bibliotecas()
    
    # Informar sobre a configuração
    logging.info(f"Sistema de logging configurado. Arquivo de log: {LOG_FILE}")
    
    return root_logger

def get_logger(name):
    """Obtém um logger configurado.
    
    Args:
        name: Nome do logger
        
    Returns:
        logging.Logger: Logger configurado
    """
    return logging.getLogger(name)

# Alias para manter compatibilidade
obter_logger = get_logger

def configurar_loggers_bibliotecas():
    """
    Configura loggers de bibliotecas externas para evitar poluição da saída.
    """
    # Configurar logger de HTTP do OpenAI para WARNING (oculta mensagens INFO)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("openai.http_client").setLevel(logging.WARNING)
    logging.getLogger("openai._base_client").setLevel(logging.WARNING)
    
    # Configurar loggers de outras bibliotecas HTTP
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

def configurar_nivel_logger(nome, nivel):
    """
    Configura o nível de logging para um logger específico.
    
    Args:
        nome: Nome do logger
        nivel: Nível de logging (ex: logging.INFO)
    """
    logger = logging.getLogger(nome)
    logger.setLevel(nivel)
    
    # Também configura manipuladores
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, RotatingFileHandler):
            handler.setLevel(nivel)
    
    return True

def definir_nivel_log(nivel):
    """
    Define o nível de log para o logger raiz.
    
    Args:
        nivel: Nível de log (logging.DEBUG, logging.INFO, etc.)
    """
    logging.getLogger().setLevel(nivel)
    
    # Atualiza também o console handler para o mesmo nível
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, RotatingFileHandler):
            handler.setLevel(nivel)
    
    return True 