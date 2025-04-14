#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para testar a execução de um agente TESS a partir de uma URL.
"""

import os
import sys
import logging
import json
from urllib.parse import urlparse, parse_qs

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar funções do script test_api_tess.py
try:
    from tests.test_api_tess import executar_agente
except ImportError:
    print("Erro: Não foi possível importar o módulo test_api_tess.py")
    sys.exit(1)

# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_tess_url(url):
    """
    Analisa uma URL do TESS e extrai o slug do agente e parâmetros.
    
    Args:
        url: URL do formato @https://agno.pareto.io/pt-BR/dashboard/user/ai/chat/ai-chat/professional-dev-ai?temperature=0&model=...
        
    Returns:
        Tupla com (slug do agente, dicionário de parâmetros)
    """
    try:
        # Remover o @ inicial se presente
        if url.startswith('@'):
            url = url[1:]
            
        # Verificar se é uma URL válida do TESS
        if not url.startswith('https://agno.pareto.io/'):
            return None, None
            
        # Extrair o slug do agente
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split('/')
        
        # O slug geralmente está na última parte do caminho
        slug = path_parts[-1]
        
        # Extrair parâmetros da query string
        params = {}
        query_params = parse_qs(parsed_url.query)
        
        # Converter parâmetros de lista para valores únicos
        for key, value in query_params.items():
            if value and len(value) > 0:
                params[key] = value[0]
                
        logger.info(f"URL TESS parseada: slug={slug}, params={params}")
        
        return slug, params
    except Exception as e:
        logger.error(f"Erro ao analisar URL TESS: {e}")
        return None, None

def main():
    # Verificar se foi fornecida uma URL
    if len(sys.argv) < 2:
        print("Uso: python test_tess_url.py <URL> [mensagem]")
        sys.exit(1)
        
    # Obter URL e mensagem opcional
    url = sys.argv[1]
    mensagem = sys.argv[2] if len(sys.argv) > 2 else "Olá, como posso ajudar? Estou testando o modelo de pensamento."
    
    # Analisar a URL
    slug, params = parse_tess_url(url)
    
    if not slug:
        print("Erro: Não foi possível extrair o slug do agente da URL.")
        sys.exit(1)
        
    logger.info(f"Executando agente: {slug}")
    logger.info(f"Parâmetros: {json.dumps(params, indent=2)}")
    logger.info(f"Mensagem: {mensagem}")
    
    # Configurar parâmetros específicos para a execução
    specific_params = {
        "temperature": params.get("temperature", "0.5"),
        "model": params.get("model", "agno-5-pro"),
        "tools": params.get("tools", "no-tools"),
        "messages": [
            {"role": "user", "content": mensagem}
        ],
        "waitExecution": True
    }
    
    # Executar o agente
    print(f"Executando agente TESS: {slug}...")
    success, data = executar_agente(slug, mensagem, is_cli=False, specific_params=specific_params)
    
    if success and "output" in data:
        print(f"\n--- Resposta do agente ---\n")
        print(data["output"])
        print("\n------------------------\n")
    else:
        error_msg = data.get('error', 'Erro desconhecido')
        print(f"Erro ao executar agente TESS: {error_msg}")
        
        # Exibir detalhes da resposta para diagnóstico
        if "full_response" in data:
            print("\nDetalhes da resposta:")
            print(json.dumps(data["full_response"], indent=2))

if __name__ == "__main__":
    main() 