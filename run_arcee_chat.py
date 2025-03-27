#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script wrapper para executar o chat do Arcee com ajuste de PYTHONPATH
"""

import os
import sys

# Obter o diretório atual
current_dir = os.path.dirname(os.path.abspath(__file__))

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, current_dir)

# Importar o módulo de chat
from crew.arcee_chat import chat

if __name__ == "__main__":
    # Executar o chat
    chat() 