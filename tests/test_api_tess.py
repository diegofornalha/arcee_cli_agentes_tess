#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste para a API HTTP do TESS
"""

import requests
import os
import json
import sys
import time
import logging
from dotenv import load_dotenv

# Configurar sistema de logging
logger = logging.getLogger("tess_api")
logger.setLevel(logging.INFO)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)

# Handler para arquivo (opcional)
try:
    log_dir = os.path.expanduser("~/.arcee/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "tess_api.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    logger.info(f"Sistema de logging configurado. Arquivo de log: {log_file}")
except Exception as e:
    logger.warning(f"Não foi possível configurar o log em arquivo: {e}")

# Carregar variáveis de ambiente
load_dotenv()
logger.info("Variáveis de ambiente carregadas")

# Constantes
DEFAULT_TIMEOUT = 60  # Timeout padrão para requisições em segundos
POLLING_INTERVAL = 5  # Intervalo entre verificações em segundos
MAX_RETRIES = 12      # Número máximo de tentativas (60 segundos)

def listar_agentes(is_cli=True, filter_type=None, keyword=None):
    """Testa a API do TESS para listar agentes
    
    Args:
        is_cli: Se True, imprime resultados no console. Se False, retorna dados.
        filter_type: Filtrar por tipo de agente (ex: 'chat', 'completion', etc.)
        keyword: Filtrar por palavra-chave no título ou descrição
        
    Returns:
        Tupla com (success, response_data)
    """
    
    # Obter a chave de API do ambiente
    api_key = os.getenv("TESS_API_KEY")

    if not api_key:
        error_msg = 'ERRO: Chave API do TESS não encontrada nas variáveis de ambiente'
        if is_cli:
            logger.error(error_msg)
        return False, {"error": error_msg}

    # Configuração da requisição
    url = 'https://tess.pareto.io/api/agents'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # Parâmetros opcionais
    params = {
        'page': 1,
        'per_page': 50  # Aumentado para capturar mais agentes
    }
    
    # Adicionar tipo ao parâmetro se especificado
    if filter_type:
        params['type'] = filter_type

    if is_cli:
        tipo_msg = f" do tipo '{filter_type}'" if filter_type else ""
        keyword_msg = f" com palavra-chave '{keyword}'" if keyword else ""
        logger.info(f'Realizando requisição para listar agentes TESS{tipo_msg}{keyword_msg}...')
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()  # Levanta exceção para erros HTTP
        
        # Formata e exibe a resposta
        data = response.json()
        
        # Filtragem adicional de tipo - caso a API não suporte filtro por tipo no parâmetro
        if filter_type and 'data' in data:
            original_count = len(data.get('data', []))
            filtered_agents = [agent for agent in data['data'] if agent.get('type', '').lower() == filter_type.lower()]
            data['data'] = filtered_agents
            filtered_count = len(data.get('data', []))
            if is_cli and original_count != filtered_count:
                logger.info(f"Filtro adicional aplicado: {filtered_count} de {original_count} agentes são do tipo '{filter_type}'")
        
        # Filtragem adicional por palavra-chave no título ou descrição
        if keyword and 'data' in data:
            keyword_lower = keyword.lower()
            original_count = len(data.get('data', []))
            filtered_agents = []
            
            for agent in data['data']:
                title = agent.get('title', '').lower()
                description = agent.get('description', '').lower()
                slug = agent.get('slug', '').lower()
                
                if (keyword_lower in title or 
                    keyword_lower in description or 
                    keyword_lower in slug):
                    filtered_agents.append(agent)
            
            data['data'] = filtered_agents
            filtered_count = len(data.get('data', []))
            if is_cli and original_count != filtered_count:
                logger.info(f"Filtro por palavra-chave '{keyword}' aplicado: {filtered_count} de {original_count} agentes contêm essa palavra")
        
        if is_cli:
            logger.info(f'Status: {response.status_code}')
            logger.info(f'Total de agentes: {len(data.get("data", []))}')
            print('\nLista de agentes:')
            
            for i, agent in enumerate(data.get('data', []), 1):
                print(f'\n{i}. {agent.get("title", "Sem título")}')
                print(f'   ID: {agent.get("id", "N/A")}')
                print(f'   Slug: {agent.get("slug", "N/A")}')
                print(f'   Descrição: {agent.get("description", "Sem descrição")}')
                print(f'   Tipo: {agent.get("type", "N/A")}')
            
            if '--verbose' in sys.argv:
                print('\nResposta completa:')
                print(json.dumps(data, indent=2))
        
        return True, data
        
    except requests.exceptions.RequestException as e:
        error_msg = f'Falha na requisição: {e}'
        if is_cli:
            logger.error(error_msg)
        return False, {"error": error_msg}

def executar_agente(agent_id, mensagem, is_cli=True, specific_params=None):
    """Testa a API do TESS para executar um agente
    
    Args:
        agent_id: ID ou slug do agente
        mensagem: Mensagem a ser processada
        is_cli: Se True, imprime resultados no console. Se False, retorna dados.
        specific_params: Parâmetros específicos para o agente (opcional)
        
    Returns:
        Tupla com (success, response_data)
    """
    
    # Obter a chave de API do ambiente
    api_key = os.getenv("TESS_API_KEY")

    if not api_key:
        error_msg = 'ERRO: Chave API do TESS não encontrada nas variáveis de ambiente'
        if is_cli:
            logger.error(error_msg)
        return False, {"error": error_msg}
        
    # Converter slug ou nome para ID numérico se necessário
    id_numerico = agent_id
    
    # Mapeamento de slugs para IDs numéricos (conforme vimos na listagem de agentes)
    slug_para_id = {
        "e-mail-de-venda-Sxtjz8": "53",
        "titulo-de-email-para-anuncio-de-novo-recurso-fDba8a": "52",
        "e-mail-de-solicitacao-de-review-pos-venda-ihvlWw": "55",
        "palavras-chave-para-campanha-de-marca-96zlo7": "59",
        "palavras-chave-para-campanha-de-produtosservicos-egK882": "60",
        "transformar-texto-em-post-para-linkedin-mF37hV": "67",
        "ideias-de-anuncios-para-o-youtube-ads-RVm1a8": "68",
        "roteiro-para-anuncio-de-video-no-youtube-ads-9pdCVJ": "69",
        "multi-chat-S7C0WU": "3176",
        "professional-dev-ai": "3238"
    }
    
    # Verificar se o ID é um slug e convertê-lo
    if agent_id in slug_para_id:
        id_numerico = slug_para_id[agent_id]
        if is_cli:
            logger.info(f"Convertendo slug '{agent_id}' para ID numérico: {id_numerico}")
    # Verificar se o ID é já um valor numérico
    elif not agent_id.isdigit() and not agent_id.startswith(("agent-", "user-")):
        # Se não está no mapeamento e não é um ID numérico, tentar buscar na lista de agentes
        try:
            success, data = listar_agentes(is_cli=False)
            if success:
                encontrado = False
                tipo_agente = ""  # Inicializar a variável para evitar erro
                for agent in data.get('data', []):
                    if agent.get('slug') == agent_id:
                        id_numerico = agent.get('id')
                        tipo_agente = agent.get('type', '')
                        encontrado = True
                        if is_cli:
                            logger.info(f"Encontrado na lista de agentes: '{agent_id}' = ID {id_numerico}, Tipo: {tipo_agente}")
                        break
                
                if not encontrado and is_cli:
                    logger.warning(f"Slug '{agent_id}' não encontrado na lista de agentes - tentando usar diretamente")
        except Exception as e:
            if is_cli:
                logger.error(f"Erro ao buscar lista de agentes: {e}")

    # Configuração da requisição
    url = f'https://tess.pareto.io/api/agents/{id_numerico}/execute'
    
    # Para agentes de chat, mantemos o mesmo endpoint mas usamos formato de parâmetros diferente
    is_chat_agent = False
    if agent_id.lower().startswith("chat-") or agent_id == "chat" or agent_id == "professional-dev-ai" or agent_id == "multi-chat-S7C0WU" or (tipo_agente and tipo_agente == "chat"):
        is_chat_agent = True
        if is_cli:
            logger.info("Detectado um agente de chat, usando formato de mensagens compatível com chat")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # Se temos parâmetros específicos, usá-los diretamente
    if specific_params:
        data = specific_params
    else:
        # Dados base para a execução
        data = {}
        
        # Adicionar parâmetros específicos baseado no tipo de agente
        if agent_id == "e-mail-de-venda-Sxtjz8" or id_numerico == "53":
            # Parâmetros para o agente de email de venda conforme documentação
            data = {
                "temperature": 0.5,
                "model": "tess-ai-light",
                "maxlength": 500,
                "language": "Portuguese (Brazil)",
                "nome-do-produto": "TESS AI",
                "url-do-produto": "https://tess.pareto.io",
                "diferenciais-do-produto": mensagem,
                "waitExecution": True
            }
        elif agent_id == "titulo-de-email-para-anuncio-de-novo-recurso-fDba8a" or id_numerico == "52":
            # Parâmetros para o agente de título de email
            data = {
                "temperature": 0.5,
                "model": "tess-ai-light",
                "maxlength": 500,
                "language": "Portuguese (Brazil)",
                "novo-recurso": "Integração com API via MCP",
                "produto": "TESS AI",
                "waitExecution": True
            }
        elif agent_id == "transformar-texto-em-post-para-linkedin-mF37hV" or id_numerico == "67":
            # Parâmetros para o agente de post LinkedIn
            data = {
                "temperature": 0.5,
                "model": "tess-ai-light",
                "maxlength": 500,
                "language": "Portuguese (Brazil)",
                "texto": mensagem,
                "waitExecution": True
            }
        elif agent_id == "ideias-de-anuncios-para-o-youtube-ads-RVm1a8" or id_numerico == "68":
            # Parâmetros para o agente de ideias de anúncios para YouTube
            data = {
                "temperature": 1,
                "model": "tess-ai-light",
                "maxlength": 750,
                "language": "Portuguese (Brazil)",
                "tema-do-anuncio": mensagem,
                "area-de-atucao-da-empresa": "Educação e Treinamento",
                "publico-alvo": "Profissionais buscando aprimoramento em marketing digital",
                "ocasiao-especial": "Lançamento do curso",
                "descreva-o-produto-ou-servico": "Curso completo de marketing digital com conteúdo prático",
                "company-name": "Academia de Marketing Digital",
                "waitExecution": True
            }
        elif agent_id.lower().startswith("chat-") or agent_id == "chat" or agent_id == "professional-dev-ai" or agent_id == "multi-chat-S7C0WU" or (tipo_agente and tipo_agente == "chat"):
            # Parâmetros para agentes do tipo chat no formato TESS
            modelo = "tess-5-pro"
            temperatura = "0.5"
            ferramentas = "no-tools"
            
            # Configurações específicas para o multi-chat-S7C0WU com Claude
            if agent_id == "multi-chat-S7C0WU":
                modelo = "claude-3-7-sonnet-latest-thinking"
                temperatura = "1"
                if is_cli:
                    logger.info(f"Usando modelo específico: {modelo} com temperatura {temperatura}")
            
            # Configurações específicas para o professional-dev-ai com Claude
            if agent_id == "professional-dev-ai":
                modelo = "claude-3-7-sonnet-latest"
                temperatura = "0"
                ferramentas = "internet"
                if is_cli:
                    logger.info(f"Usando modelo específico: {modelo} com temperatura {temperatura} e ferramentas: {ferramentas}")
            
            data = {
                "temperature": temperatura,
                "model": modelo,
                "messages": [
                    {"role": "user", "content": mensagem}
                ],
                "tools": ferramentas,
                "waitExecution": True
            }
            
            if is_cli:
                logger.info("Executando no modo chat...")
        else:
            # Caso genérico, usa o conteúdo da mensagem diretamente
            data = {
                "temperature": 0.5,
                "model": "tess-ai-light",
                "maxlength": 500,
                "language": "Portuguese (Brazil)",
                "mensagem": mensagem,
                "texto": mensagem,  # Adicionar texto como alternativa comum
                "waitExecution": True
            }
    
    # Garantir que waitExecution esteja definido
    if "waitExecution" not in data:
        data["waitExecution"] = True
    
    if is_cli:
        logger.info(f'Executando agente TESS (ID: {id_numerico})...')
        logger.info(f'Usando URL: {url}')
        
        if '--verbose' in sys.argv:
            print(f'Parâmetros: {json.dumps(data, indent=2, ensure_ascii=False)}')
    
    try:
        # Submete a requisição para iniciar a execução
        response = requests.post(url, headers=headers, json=data, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()  # Levanta exceção para erros HTTP
        
        # Captura a resposta inicial
        result = response.json()
        
        if is_cli:
            logger.info(f'Status: {response.status_code}')
        
        # Processamento especial para agentes de chat
        if is_chat_agent:
            # Verificar se a resposta contém o formato esperado para chat
            if 'output' in result:
                output_text = result['output']
                
                if is_cli:
                    logger.info('A execução foi concluída com sucesso!')
                    print('\nResposta do agente de chat:')
                    print(output_text)
                    
                    if '--verbose' in sys.argv:
                        print('\nDetalhes completos:')
                        print(json.dumps(result, indent=2, ensure_ascii=False))
                
                return True, {"output": output_text, "full_response": result}
            else:
                # Tentar encontrar a resposta em outros campos comuns
                if 'responses' in result and len(result['responses']) > 0:
                    response_data = result['responses'][0]
                    if 'output' in response_data:
                        output_text = response_data['output']
                        
                        if is_cli:
                            logger.info('A execução foi concluída com sucesso!')
                            print('\nResposta do agente de chat:')
                            print(output_text)
                            
                            if '--verbose' in sys.argv:
                                print('\nDetalhes completos:')
                                print(json.dumps(result, indent=2, ensure_ascii=False))
                        
                        return True, {"output": output_text, "full_response": result}
                
                # Se não encontramos o output em nenhum lugar, retornar a resposta bruta
                if is_cli:
                    logger.warning('Formato de resposta inesperado para agente de chat!')
                    print('\nResposta completa:')
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                
                return True, {"full_response": result}
        
        # Com waitExecution=true, o resultado já deve estar disponível para agentes regulares
        elif 'responses' in result and len(result['responses']) > 0:
            response_data = result['responses'][0]
            
            # Verifica se o status é "succeeded" e se há output
            if response_data.get('status') == 'succeeded' and response_data.get('output'):
                output_text = response_data['output']
                
                if is_cli:
                    logger.info('A execução foi concluída com sucesso!')
                    print('\nResposta do agente:')
                    print(output_text)
                    
                    if '--verbose' in sys.argv:
                        print('\nDetalhes completos:')
                        print(json.dumps(response_data, indent=2, ensure_ascii=False))
                
                return True, {"output": output_text, "full_response": response_data}
            
            # Se ainda não estiver pronto, mostra o ID para polling manual
            execution_id = response_data.get('id')
            if execution_id:
                if is_cli:
                    print(f'ID de execução: {execution_id}')
                
                # Verifica se waitExecution foi configurado como true
                input_data = response_data.get('input', {})
                if input_data.get('waitExecution') == True and is_cli:
                    logger.warning("A opção waitExecution=true foi definida, mas a API não retornou o resultado completo.")
                    logger.warning("Isso pode indicar que a execução ainda está em andamento ou que houve um problema.")
                
                # Se waitExecution=true não funcionou, tentamos polling
                if response_data.get('status') != 'succeeded':
                    if is_cli:
                        logger.info('Aguardando conclusão da execução...')
                    
                    # URL para verificar o status da execução
                    status_url = f'https://tess.pareto.io/api/agents/{id_numerico}/executions/{execution_id}'
                    
                    # Loop para verificar periodicamente o resultado
                    retries = 0
                    while retries < MAX_RETRIES:
                        time.sleep(POLLING_INTERVAL)
                        if is_cli:
                            logger.info(f'Verificando status (tentativa {retries+1}/{MAX_RETRIES})...')
                        
                        try:
                            status_response = requests.get(status_url, headers=headers, timeout=DEFAULT_TIMEOUT)
                            status_response.raise_for_status()
                            status_result = status_response.json()
                            
                            # Verifica se a execução está concluída
                            status = status_result.get('status', '')
                            if status == 'completed':
                                output_text = status_result.get('output', '')
                                
                                if is_cli:
                                    logger.info('Execução concluída!')
                                    
                                    if output_text:
                                        print('\nResposta do agente:')
                                        print(output_text)
                                    
                                    if '--verbose' in sys.argv:
                                        print('\nResposta completa:')
                                        print(json.dumps(status_result, indent=2, ensure_ascii=False))
                                
                                return True, {"output": output_text, "full_response": status_result}
                            elif status == 'failed':
                                if is_cli:
                                    logger.error('A execução falhou!')
                                    if '--verbose' in sys.argv:
                                        print(json.dumps(status_result, indent=2, ensure_ascii=False))
                                
                                return False, {"error": "Execução falhou", "details": status_result}
                            else:
                                if is_cli:
                                    logger.info(f'Status atual: {status}')
                        except requests.exceptions.RequestException as e:
                            if is_cli:
                                logger.error(f'Erro ao verificar status: {e}')
                        
                        retries += 1
                    
                    if is_cli:
                        logger.warning('Tempo limite de espera excedido!')
        
        # Se não conseguimos o ID de execução ou o loop de verificação terminou sem conclusão, 
        # mostramos a resposta inicial
        if is_cli:
            if '--verbose' in sys.argv:
                print('\nResposta inicial:')
                print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return True, {"partial_result": result}
        
    except requests.exceptions.RequestException as e:
        error_msg = f'Falha na requisição: {e}'
        error_details = {}
        
        if is_cli:
            logger.error(error_msg)
            
            if hasattr(e, 'response') and e.response is not None:
                logger.error('Detalhes do erro:')
                try:
                    erro_detalhes = e.response.json()
                    error_details = erro_detalhes
                    if '--verbose' in sys.argv:
                        print(json.dumps(erro_detalhes, indent=2, ensure_ascii=False))
                except:
                    status_code = e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'
                    error_text = e.response.text if hasattr(e.response, 'text') else 'N/A'
                    logger.error(f'Status: {status_code}')
                    logger.error(f'Texto: {error_text}')
                    error_details = {"status": status_code, "text": error_text}
        
        return False, {"error": error_msg, "details": error_details}

def printar_help():
    """Exibe ajuda sobre como usar o script"""
    print('Uso: python test_api_tess.py COMANDO [ARGS]')
    print('')
    print('Comandos disponíveis:')
    print('  executar AGENT_ID MENSAGEM  - Execute um agente TESS com a mensagem fornecida')
    print('  listar                      - Lista todos os agentes disponíveis')
    print('  listar-chat                 - Lista apenas os agentes do tipo "chat"')
    print('  listar-keyword KEYWORD       - Lista agentes contendo a palavra-chave especificada')
    print('  listar-chat-keyword KEYWORD  - Lista agentes do tipo "chat" contendo a palavra-chave especificada')
    print('  help                        - Exibe esta ajuda')
    print('')
    print('Opções:')
    print('  --verbose                   - Mostra informações detalhadas e respostas completas')
    print('')
    print('Exemplos:')
    print('  python test_api_tess.py executar e-mail-de-venda-Sxtjz8 "Minha mensagem aqui"')
    print('  python test_api_tess.py executar 53 "Minha mensagem aqui"')
    print('  python test_api_tess.py executar multi-chat-S7C0WU "Olá, como posso ajudar hoje?"')
    print('  python test_api_tess.py executar professional-dev-ai "Faça um resumo sobre IA"')
    print('  python test_api_tess.py listar')
    print('  python test_api_tess.py listar-chat')
    print('  python test_api_tess.py listar-keyword linkedin')
    print('  python test_api_tess.py listar-chat-keyword linkedin')

def main():
    """Função principal para processar argumentos da linha de comando"""
    
    # Verificar se os argumentos foram fornecidos
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        print("\nUso: python test_api_tess.py COMANDO [ARGUMENTOS]")
        print("\nComandos disponíveis:")
        print("  listar                 - Lista todos os agentes disponíveis")
        print("  listar-chat            - Lista apenas os agentes do tipo 'chat'")
        print("  listar-keyword KEYWORD - Lista agentes contendo a palavra-chave especificada")
        print("  listar-chat-keyword KEYWORD - Lista agentes do tipo 'chat' contendo a palavra-chave especificada")
        print("  executar AGENT_ID MENSAGEM - Executa um agente específico com a mensagem fornecida")
        print("  help                   - Exibe esta mensagem de ajuda")
        print("\nExemplos:")
        print("  python test_api_tess.py listar")
        print("  python test_api_tess.py listar-chat")
        print("  python test_api_tess.py listar-keyword linkedin")
        print("  python test_api_tess.py listar-chat-keyword linkedin")
        print("  python test_api_tess.py executar transformar-texto-em-post-para-linkedin-mF37hV \"Texto para transformar em post\"")
        print("  python test_api_tess.py executar multi-chat-S7C0WU \"Pergunta para o chat\"")
        return
    
    # Processar comandos
    comando = sys.argv[1].lower()
    
    if comando == "listar":
        listar_agentes()
    elif comando == "listar-chat":
        listar_agentes(filter_type="chat")
    elif comando == "listar-keyword" and len(sys.argv) >= 3:
        keyword = sys.argv[2]
        listar_agentes(keyword=keyword)
    elif comando == "listar-chat-keyword" and len(sys.argv) >= 3:
        keyword = sys.argv[2]
        listar_agentes(filter_type="chat", keyword=keyword)
    elif comando == "executar":
        # Verificar se os argumentos necessários foram fornecidos
        if len(sys.argv) < 4:
            print("ERRO: Argumentos insuficientes para o comando 'executar'")
            print("Uso: python test_api_tess.py executar AGENT_ID MENSAGEM")
            return
            
        agent_id = sys.argv[2]
        mensagem = sys.argv[3]
        
        # Se houver mais argumentos, juntar como parte da mensagem
        if len(sys.argv) > 4:
            mensagem = " ".join(sys.argv[3:])
        
        executar_agente(agent_id, mensagem)
    else:
        print(f"ERRO: Comando desconhecido: {comando}")
        print("Use 'python test_api_tess.py help' para ver a lista de comandos disponíveis")

if __name__ == '__main__':
    main() 