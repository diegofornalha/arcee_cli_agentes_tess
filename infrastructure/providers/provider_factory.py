#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fábrica para criar provedores de IA
"""

from typing import Optional
from .arcee_provider import ArceeProvider
from .tess_provider import TessProvider

# Provedor global para ser reutilizado em diferentes comandos
_provider = None


def get_provider(api_key: Optional[str] = None, api_url: Optional[str] = None):
    """Retorna uma instância do provedor global"""
    global _provider
    
    if not _provider:
        try:
            _provider = ArceeProvider(api_key, api_url)
        except Exception as e:
            print(f"❌ Erro ao inicializar provedor: {str(e)}")
    return _provider

def create_provider(provider_type: str, api_key: Optional[str] = None, api_url: Optional[str] = None):
    """Cria uma instância do provedor solicitado"""
    
    if provider_type.lower() == "arcee":
        return ArceeProvider(api_key, api_url)
    elif provider_type.lower() == "agno":
        return TessProvider(api_key, api_url)
    else:
        raise ValueError(f"Provedor não suportado: {provider_type}")
