#!/usr/bin/env python
"""
Processador de Linguagem Natural para o MCP (Module Command Processor)

Este módulo intercepta comandos em linguagem natural relacionados ao MCP
durante o chat e os traduz em ações.
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import os
from pathlib import Path
import time
import webbrowser  # Importar módulo para abrir URLs no navegador
import io
import sys
from contextlib import redirect_stdout
import requests
import urllib.parse

# Importar o cliente MCP simplificado
try:
    from .mcpx_simple import MCPRunClient, configure_mcprun
    MCPRUN_SIMPLE_AVAILABLE = True
except ImportError:
    MCPRUN_SIMPLE_AVAILABLE = False

from ..providers.mcp_provider import MCPProvider

# Importar funções do script test_api_tess.py
try:
    from tests.test_api_tess import listar_agentes, executar_agente
    TEST_API_TESS_AVAILABLE = True
except ImportError:
    TEST_API_TESS_AVAILABLE = False

# Configurar logger
logger = logging.getLogger(__name__)

# URLs para o dashboard do TESS
TESS_DASHBOARD_URLS = {
    "transformar-texto-em-post-para-linkedin-mF37hV": "https://tess.pareto.io/pt-BR/dashboard/user/ai/generator/transformar-texto-em-post-para-linkedin-mF37hV",
    "e-mail-de-venda-Sxtjz8": "https://tess.pareto.io/pt-BR/dashboard/user/ai/generator/e-mail-de-venda-Sxtjz8",
    "titulo-de-email-para-anuncio-de-novo-recurso-fDba8a": "https://tess.pareto.io/pt-BR/dashboard/user/ai/generator/titulo-de-email-para-anuncio-de-novo-recurso-fDba8a",
    "e-mail-de-solicitacao-de-review-pos-venda-ihvlWw": "https://tess.pareto.io/pt-BR/dashboard/user/ai/generator/e-mail-de-solicitacao-de-review-pos-venda-ihvlWw",
    "palavras-chave-para-campanha-de-marca-96zlo7": "https://tess.pareto.io/pt-BR/dashboard/user/ai/generator/palavras-chave-para-campanha-de-marca-96zlo7",
    "palavras-chave-para-campanha-de-produtosservicos-egK882": "https://tess.pareto.io/pt-BR/dashboard/user/ai/generator/palavras-chave-para-campanha-de-produtosservicos-egK882"
}

def parse_tess_url(url: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Analisa uma URL do TESS e extrai o slug do agente e parâmetros.
    
    Args:
        url: URL do formato @https://tess.pareto.io/pt-BR/dashboard/user/ai/chat/ai-chat/professional-dev-ai?temperature=0&model=claude-3-7-sonnet-latest&tools=internet#
        
    Returns:
        Tupla com (slug do agente, dicionário de parâmetros)
    """
    try:
        # Remover o @ inicial se presente
        if url.startswith('@'):
            url = url[1:]
            
        # Verificar se é uma URL válida do TESS
        if not url.startswith('https://tess.pareto.io/'):
            return None, None
            
        # Extrair o slug do agente
        parsed_url = urllib.parse.urlparse(url)
        path_parts = parsed_url.path.split('/')
        
        # O slug geralmente está na última parte do caminho
        slug = path_parts[-1]
        
        # Extrair parâmetros da query string
        params = {}
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Converter parâmetros de lista para valores únicos
        for key, value in query_params.items():
            if value and len(value) > 0:
                params[key] = value[0]
                
        # Logger para debug
        logger.info(f"URL TESS parseada: slug={slug}, params={params}")
        
        return slug, params
    except Exception as e:
        logger.error(f"Erro ao analisar URL TESS: {e}")
        return None, None

class MCPNLProcessor:
    """
    Processador de comandos em linguagem natural para o MCP.
    
    Esta classe detecta e processa comandos em linguagem natural relacionados
    ao MCP durante o chat e executa as ações correspondentes.
    """
    
    def __init__(self, agent=None):
        """
        Inicializa o processador de comandos do MCP.
        Define expressões regulares para processar comandos.
        
        Args:
            agent: Agente (opcional)
        """
        # Armazenar informações do agente
        self.agent = agent
        
        # Flag para ativar processamento com LLM
        self.usar_llm_para_tess = False
        
        # Cache para reduzir chamadas à API
        self.cache = {}
        self.cache_ttl = 300  # 5 minutos
        
        # Padrões de expressões regulares para comandos
        self.comandos_padroes = [
            # Buscar agentes TESS por palavras-chave
            (r'(buscar?|procurar?|encontrar?|pesquisar?)\s+(agentes?|templates?|modelos?)\s+(do\s+)?(tess|tessai)(\s+com\s+|\s+sobre\s+|\s+para\s+|\s+relacionado\s+(a|com|ao)\s+|\s+de\s+)(?P<termo>[a-zA-Z0-9_\s-]+)', 'buscar_agentes'),
            
            # Buscar agentes TESS por tipo específico
            (r'(buscar?|procurar?|encontrar?|pesquisar?)\s+(agentes?|templates?|modelos?)\s+(do\s+)?(tipo\s+)?(?P<tipo>chat|text|completion)(\s+(do|da|no|na)\s+(tess|tessai))?', 'buscar_agentes_por_tipo'),
            
            # Buscar agentes TESS por tipo específico e termo
            (r'(buscar?|procurar?|encontrar?|pesquisar?)\s+(agentes?|templates?|modelos?)\s+(do\s+)?(tipo\s+)?(?P<tipo>chat|text|completion)(\s+(do|da|no|na)\s+(tess|tessai))?(\s+com\s+|\s+sobre\s+|\s+para\s+|\s+relacionado\s+(a|com|ao)\s+|\s+de\s+)(?P<termo>[a-zA-Z0-9_\s-]+)', 'buscar_agentes_por_tipo_e_termo'),
            
            # Novo: Listar agentes com uma palavra-chave específica
            (r'(listar?|mostrar?|exibir?|ver?)\s+(agentes?|templates?|modelos?)\s+(com|contendo|sobre|relacionado\s+(a|com|ao))\s+(?P<keyword>[a-zA-Z0-9_\s-]+)', 'listar_agentes_por_keyword'),
            
            # Novo: Listar agentes de um tipo com uma palavra-chave específica
            (r'(listar?|mostrar?|exibir?|ver?)\s+(agentes?|templates?|modelos?)\s+(do\s+)?(tipo\s+)?(?P<tipo>chat|text|completion)(\s+(do|da|no|na)\s+(tess|tessai))?(\s+(com|contendo|sobre|relacionado\s+(a|com|ao)))\s+(?P<keyword>[a-zA-Z0-9_\s-]+)', 'listar_agentes_por_tipo_e_keyword'),
            
            # Novo: Capturar formato simplificado "agentes <keyword>" sem palavras de ligação
            (r'^(listar?|mostrar?|exibir?|ver?)?\s*(agentes?|templates?|modelos?)\s+(?P<keyword>[a-zA-Z0-9_\s-]{3,})$', 'listar_agentes_por_keyword'),
            
            # Executar agente TESS específico
            (r'(executar?|rodar?|usar?)\s+(o\s+)?(agente|template|modelo)\s+(do\s+)?(tess|tessai)\s+(?P<id>[a-zA-Z0-9_-]+)(\s+com\s+(mensagem|texto)\s+(?P<mensagem>[^$]+))?', 'executar_agente_tess'),
            
            # Transformar texto em post LinkedIn (comando direto)
            (r'(transformar?|converter?|criar?)\s+(esse\s+|este\s+)?(texto|conteúdo|mensagem)\s+em\s+(post|publicação)\s+(para|do)\s+linkedin:?\s*(?P<texto>.+)', 'transformar_post_linkedin'),
            
            # Criar email de venda (comando direto)
            (r'(criar?|gerar?|escrever?)\s+(um\s+)?(email|e-mail|mail)\s+de\s+venda\s+(para|sobre):?\s*(?P<produto>.+)', 'criar_email_venda'),
            
            # Comandos simples de ajuda
            (r'(mostrar?|ver?|listar?)\s+(comandos|opções|ajuda)', 'mostrar_ajuda'),
            
            # Listar todos os agentes TESS
            (r'(mostrar?|exibir?|listar?|ver?)\s+(todos\s+)?(os\s+)?(agentes?|templates?|modelos?)\s+(do\s+)?(tess|tessai)', 'listar_todos_agentes'),
            
            # Listar apenas agentes de chat
            (r'(mostrar?|exibir?|listar?|ver?|filtrar?)\s+(os\s+)?agentes?\s+(do\s+)?(tipo\s+)?chat(\s+(do|da|no|na)\s+(tess|tessai))?', 'listar_agentes_chat'),
            
            # Novo: Testar API TESS para listar agentes
            (r'(testar?|usar?|executar?)\s+(a\s+)?api\s+(do\s+)?tess(\s+para)?\s+(listar|mostrar|exibir)\s+(os\s+)?(agentes?|templates?)', 'testar_api_listar_agentes'),
            
            # Novo: Testar API TESS para listar agentes do tipo chat
            (r'(testar?|usar?|executar?)\s+(a\s+)?api\s+(do\s+)?tess(\s+para)?\s+(listar|mostrar|exibir)\s+(os\s+)?agentes?\s+(do\s+)?(tipo\s+)?chat', 'testar_api_listar_agentes_chat'),
            
            # Novo: Testar API TESS para executar agente específico
            (r'(testar?|usar?|executar?)\s+(a\s+)?api\s+(do\s+)?tess\s+(?P<id>[a-zA-Z0-9_-]+)(\s+com\s+(mensagem|texto)\s+(?P<mensagem>[^$]+))', 'testar_api_executar_agente'),
            
            # Novo: Comando abreviado para testar API
            (r'test_api_tess\s+(listar|executar)(\s+(?P<id>[a-zA-Z0-9_-]+))?(\s+(?P<mensagem>[^$]+))?', 'testar_api_tess'),
        ]
    
    def detectar_comando(self, mensagem: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Detecta se uma mensagem contém comandos do MCP

        Args:
            mensagem: Mensagem a ser analisada

        Returns:
            Tupla com (é_comando, tipo_comando, parametros)
        """
        # Se o processador LLM está ativado, procuramos por termos relacionados ao TESS
        # e enviamos para o processamento avançado com LLM se encontrarmos
        if self.usar_llm_para_tess:
            # Verificar se a mensagem contém termos relacionados ao TESS
            termos_tess = ["tess", "agente", "agentes", "ferramentas", "mcp"]
            mensagem_lower = mensagem.lower()
            if any(termo in mensagem_lower for termo in termos_tess):
                # Registrar no log
                logging.info("Detectados termos relacionados ao TESS, tentando processamento com LLM")
                # Tenta processar com LLM primeiro
                tem_comando, tipo_comando, parametros = self.processar_comando_com_llm(mensagem)
                if tem_comando:
                    # Se conseguiu detectar um comando com LLM, retorna
                    return tem_comando, tipo_comando, parametros
        
        # Detectar URLs TESS
        if mensagem.startswith('@https://tess.pareto.io/'):
            logging.info("Detectada URL TESS")
            slug, params = parse_tess_url(mensagem)
            if slug:
                # Converter para o formato de comando executar_agente
                return True, "executar_agente_tess", {
                    "agent_id": slug,
                    "params": params,
                    "mensagem": "",  # Deixamos em branco pois os parâmetros já vêm da URL
                    "is_url": True
                }

        # Detecta comandos para ferramentas MCP
        # Regex para detectar comandos do tipo: "usar ferramenta X para fazer Y"
        regex_usar_ferramenta = r"(usar|executar|rodar|iniciar)\s+(?:a\s+)?(?:ferramenta\s+)?([a-zA-Z0-9_-]+)(?:\s+(?:para|com|e)\s+(.+))?$"
        match_ferramenta = re.match(regex_usar_ferramenta, mensagem, re.IGNORECASE)
        
        # Processar comando usando expressões regulares
        for padrao, tipo_comando in self.comandos_padroes:
            match = re.search(padrao, mensagem, re.IGNORECASE)
            if match:
                # Extrair parâmetros do comando
                params = {k: v for k, v in match.groupdict().items() if v is not None}
                logging.info(f"Detectado comando TESS via regex: {tipo_comando}")
                return True, tipo_comando, params
                
        # Se não encontrou um padrão de regex, tentar processar com LLM
        return self.processar_comando_com_llm(mensagem)
    
    def processar_comando_com_llm(self, mensagem: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Processa um comando usando o LLM para interpretar a intenção do usuário.
        
        Args:
            mensagem: A mensagem do usuário
            
        Returns:
            Tupla (is_comando, tipo_comando, parametros)
        """
        try:
            # Verificar se a mensagem pode conter um comando TESS
            if len(mensagem.split()) < 2:  # Mensagens muito curtas provavelmente não são comandos
                return False, "", {}
                
            # Criar um prompt especializado para o LLM
            prompt = f"""
            Você é um assistente especializado em interpretar comandos para o sistema TESS de agentes.
            
            Analise a seguinte mensagem do usuário e determine se ela contém um comando relacionado ao TESS.
            Mensagem: "{mensagem}"
            
            Se for um comando TESS, identifique qual dos seguintes tipos de comando:
            - buscar_agentes: Para buscar agentes com um termo
            - listar_agentes: Para listar todos os agentes disponíveis
            - executar_agente: Para executar um agente com uma mensagem
            - obter_agente: Para obter detalhes de um agente específico
            - buscar_arquivos: Para buscar arquivos de um agente
            
            Para o comando "executar_agente", extraia o agent_id (ou slug) e a mensagem a ser processada.
            
            Retorne a resposta no formato JSON:
            ```json
            {{"é_comando": true/false, "tipo_comando": "tipo_do_comando", "parametros": {{"param1": "valor1", "param2": "valor2"}}}}
            ```
            
            Se for um comando "executar_agente", os parâmetros devem ser:
            ```json
            {{"agent_id": "id_ou_slug_do_agente", "mensagem": "texto da mensagem"}}
            ```
            
            Se não for um comando TESS, retorne "é_comando" como false.
            """
            
            # Chamar o LLM do Arcee (usando generate_content_chat em vez de generate_content)
            from infrastructure.providers.arcee_provider import ArceeProvider
            provider = ArceeProvider()
            
            # Criar mensagens para o formato chat
            messages = [
                {"role": "system", "content": "Você é um assistente especializado em interpretar comandos TESS."},
                {"role": "user", "content": prompt}
            ]
            
            # Usar generate_content_chat em vez de generate_content
            resposta = provider.generate_content_chat(messages)
            
            # Extrair o JSON da resposta
            import json
            import re
            
            # Obter o texto da resposta
            resposta_text = resposta.get('text', '')
            
            # Encontrar o bloco JSON na resposta
            json_match = re.search(r'```json\s+(.*?)\s+```', resposta_text, re.DOTALL)
            if not json_match:
                # Tentar procurar por JSON sem o marcador de código
                json_match = re.search(r'({.*})', resposta_text, re.DOTALL)
                if not json_match:
                    return False, "", {}
                
            json_str = json_match.group(1)
            resultado = json.loads(json_str)
            
            # Verificar se é um comando
            if not resultado.get('é_comando', False):
                return False, "", {}
                
            # Extrair tipo e parâmetros
            tipo_comando = resultado.get('tipo_comando', '')
            parametros = resultado.get('parametros', {})
            
            # Registrar no log
            logging.info(f"Detectado comando do TESS com LLM: {tipo_comando}")
            
            return True, tipo_comando, parametros
            
        except Exception as e:
            logging.error(f"Erro ao processar comando com LLM: {e}")
            return False, "", {}
    
    def processar_comando(self, tipo_comando: str, params: Dict[str, Any]) -> Optional[str]:
        """Executa o processamento do comando detectado

        Args:
            tipo_comando: Tipo de comando a ser processado
            params: Parâmetros do comando

        Returns:
            Texto de resposta ou None
        """
        # Direcionar o processamento de acordo com o tipo de comando
        if tipo_comando == "buscar_agentes":
            return self._comando_buscar_agentes(params)
        elif tipo_comando == "buscar_agentes_por_tipo":
            return self._comando_buscar_agentes_por_tipo(params)
        elif tipo_comando == "buscar_agentes_por_tipo_e_termo":
            return self._comando_buscar_agentes_por_tipo_e_termo(params)
        elif tipo_comando == "executar_agente_tess":
            agent_id = params.get("id", "")
            mensagem = params.get("mensagem", "")
            is_url = params.get("is_url", False)
            return self._comando_executar_agente_tess(agent_id, mensagem, params, is_url)
        elif tipo_comando == "transformar_post_linkedin":
            return self._comando_transformar_post_linkedin(params)
        elif tipo_comando == "criar_email_venda":
            return self._comando_criar_email_venda(params)
        elif tipo_comando == "mostrar_ajuda":
            return self._comando_mostrar_ajuda(params)
        elif tipo_comando == "listar_todos_agentes":
            return self._comando_listar_todos_agentes(params)
        elif tipo_comando == "listar_agentes_chat":
            return self._comando_listar_agentes_chat(params)
        elif tipo_comando == "testar_api_listar_agentes":
            return self._comando_testar_api_listar_agentes(params)
        elif tipo_comando == "testar_api_listar_agentes_chat":
            return self._comando_testar_api_listar_agentes_chat(params)
        elif tipo_comando == "testar_api_executar_agente":
            return self._comando_testar_api_executar_agente(params)
        elif tipo_comando == "testar_api_tess":
            return self._comando_testar_api_tess(params)
        elif tipo_comando == "listar_agentes_por_keyword":
            return self._comando_listar_agentes_por_keyword(params)
        elif tipo_comando == "listar_agentes_por_tipo_e_keyword":
            return self._comando_listar_agentes_por_tipo_e_keyword(params)
        else:
            return f"Comando não implementado: {tipo_comando}"
    
    def _comando_listar_ferramentas(self, params: Dict[str, Any]) -> str:
        """
        Lista as ferramentas disponíveis no MCP
        """
        # Verificar se o MCP está configurado
        session_id = MCPProvider.get_mcp_session_id()
        if not session_id:
            return "❌ MCP não configurado. Use 'configurar mcp' primeiro."
        
        try:
            # Criar cliente MCP
            client = MCPRunClient(session_id=session_id)
            
            # Obter ferramentas
            tools = client.get_tools()
            
            if not tools:
                return "ℹ️ Nenhuma ferramenta MCP disponível para esta sessão."
            
            # Formatar resposta
            resultado = "📋 **Ferramentas MCP disponíveis:**\n\n"
            
            for i, tool in enumerate(tools, 1):
                nome = tool.get('name', 'N/A')
                descricao = tool.get('description', 'Sem descrição')
                resultado += f"{i}. **{nome}**\n"
                resultado += f"   {descricao}\n\n"
            
            return resultado.strip()
            
        except Exception as e:
            logger.exception(f"Erro ao listar ferramentas MCP: {e}")
            return f"❌ Erro ao listar ferramentas: {str(e)}"
    
    def _comando_configurar_mcp(self, params: Dict[str, Any]) -> str:
        """
        Configura o MCP com um ID de sessão
        """
        session_id = params.get('session_id')
        
        try:
            # Configurar MCP
            new_session_id = configure_mcprun(session_id)
            
            if new_session_id:
                # Salvar ID de sessão
                if MCPProvider.save_mcp_session_id(new_session_id):
                    return f"✅ MCP configurado com sucesso!\nID de sessão: {new_session_id}"
                else:
                    return f"⚠️ MCP configurado, mas não foi possível salvar o ID de sessão.\nID de sessão atual: {new_session_id}"
            else:
                return "❌ Não foi possível configurar o MCP.\nVerifique os logs para mais detalhes."
                
        except Exception as e:
            logger.exception(f"Erro ao configurar MCP: {e}")
            return f"❌ Erro ao configurar MCP: {str(e)}"
    
    def _comando_executar_ferramenta(self, params: Dict[str, Any]) -> str:
        """
        Executa uma ferramenta MCP
        """
        # Obter nome da ferramenta
        nome = params.get('nome')
        if not nome:
            return "❌ Nome da ferramenta não especificado."
        
        # Obter parâmetros (se fornecidos)
        tool_params = params.get('params', {})
        
        # Verificar se o MCP está configurado
        session_id = MCPProvider.get_mcp_session_id()
        if not session_id:
            return "❌ MCP não configurado. Use 'configurar mcp' primeiro."
        
        try:
            # Criar cliente MCP
            client = MCPRunClient(session_id=session_id)
            
            # Executar ferramenta
            result = client.run_tool(nome, tool_params)
            
            # Verificar se houve erro
            if result.get('error'):
                return f"❌ Erro ao executar ferramenta: {result['error']}"
            
            # Formatar resposta
            return f"✅ **Resultado da ferramenta {nome}:**\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
            
        except Exception as e:
            logger.exception(f"Erro ao executar ferramenta MCP: {e}")
            return f"❌ Erro ao executar ferramenta: {str(e)}"
            
    def _comando_buscar_agentes(self, params: Dict[str, Any]) -> str:
        """
        Busca agentes TESS por termo
        
        Args:
            params: Parâmetros com termo de busca e opcionalmente um tipo
            
        Returns:
            Resposta formatada com os agentes encontrados
        """
        # Obter termo de busca
        termo = params.get('termo', '').strip()
        tipo = params.get('tipo', '').strip().lower()
        
        if not termo and not tipo:
            return "❌ Por favor, especifique um termo para buscar agentes TESS ou um tipo específico (chat, text, etc.)."
        
        # Definir mapeamento de slugs para IDs (baseado no test_api_tess.py)
        slug_para_id = {
            "e-mail-de-venda-Sxtjz8": "53",
            "titulo-de-email-para-anuncio-de-novo-recurso-fDba8a": "52",
            "e-mail-de-solicitacao-de-review-pos-venda-ihvlWw": "55",
            "palavras-chave-para-campanha-de-marca-96zlo7": "59",
            "palavras-chave-para-campanha-de-produtosservicos-egK882": "60",
            "transformar-texto-em-post-para-linkedin-mF37hV": "67"
        }
        
        # Implementar a consulta à API TESS
        try:
            # Obter a chave de API do ambiente
            api_key = os.getenv("TESS_API_KEY")
            if not api_key:
                return "❌ ERRO: Chave API do TESS não encontrada nas variáveis de ambiente. Configure a variável TESS_API_KEY."
            
            # Configuração da requisição
            url = 'https://tess.pareto.io/api/agents'
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Parâmetros de paginação
            request_params = {
                'page': 1,
                'per_page': 50  # Aumentamos para ter mais resultados
            }
            
            # Adicionar tipo ao parâmetro se especificado
            if tipo:
                request_params['type'] = tipo
                logging.info(f'Realizando requisição para buscar agentes TESS do tipo {tipo} com termo: {termo}...')
            else:
                logging.info(f'Realizando requisição para buscar agentes TESS com termo: {termo}...')
            
            # Fazer a requisição
            response = requests.get(url, headers=headers, params=request_params, timeout=30)
            response.raise_for_status()  # Levanta exceção para erros HTTP
            
            # Processar a resposta
            data = response.json()
            agentes = data.get('data', [])
            
            # Filtragem adicional de tipo - caso a API não suporte filtro por tipo no parâmetro
            if tipo and 'type' not in request_params:
                agentes_filtrados = [a for a in agentes if a.get('type', '').lower() == tipo]
                
                # Se encontrou agentes com o tipo, substitui a lista
                if agentes_filtrados:
                    agentes = agentes_filtrados
                    logging.info(f"Filtro adicional por tipo '{tipo}' aplicado: {len(agentes)} agentes")
            
            # Filtrar agentes que correspondem ao termo de busca (se houver termo)
            resultados = []
            if termo:
                for agente in agentes:
                    titulo = agente.get('title', '').lower()
                    descricao = agente.get('description', '').lower()
                    
                    if termo.lower() in titulo or termo.lower() in descricao:
                        resultados.append(agente)
            else:
                # Se não há termo de busca, usar todos os agentes já filtrados por tipo
                resultados = agentes
            
            # Formatar a resposta
            if not resultados:
                mensagem_erro = ""
                if termo and tipo:
                    mensagem_erro = f"🔍 Nenhum agente do tipo '{tipo}' encontrado para o termo de busca: \"{termo}\""
                elif tipo:
                    mensagem_erro = f"🔍 Nenhum agente do tipo '{tipo}' encontrado"
                else:
                    mensagem_erro = f"🔍 Nenhum agente encontrado para o termo de busca: \"{termo}\""
                return mensagem_erro
            
            # Texto do cabeçalho com base no filtro
            if termo and tipo:
                resposta = f"🔍 Encontrados {len(resultados)} agentes do tipo '{tipo}' para o termo \"{termo}\":\n\n"
            elif tipo:
                resposta = f"🔍 Encontrados {len(resultados)} agentes do tipo '{tipo}':\n\n"
            else:
                resposta = f"🔍 Encontrados {len(resultados)} agentes para o termo \"{termo}\":\n\n"
            
            for i, agente in enumerate(resultados, 1):
                # Obter o tipo do agente (chat, text, etc)
                tipo_agente = agente.get('type', 'desconhecido')
                tipo_icone = "💬" if tipo_agente == "chat" else "📝" if tipo_agente == "text" else "🔄"
                
                resposta += f"{i}. {agente.get('title', 'Sem título')} {tipo_icone}\n"
                resposta += f"   ID: {agente.get('id', 'N/A')}\n"
                resposta += f"   Slug: {agente.get('slug', 'N/A')}\n"
                resposta += f"   Tipo: {tipo_agente.capitalize()}\n"
                resposta += f"   Descrição: {agente.get('description', 'Sem descrição')}\n\n"
            
            resposta += "Para executar um agente, use: executar agente <slug> \"sua mensagem aqui\""
            
            return resposta
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao buscar agentes TESS: {e}")
            return f"❌ Erro ao buscar agentes: {str(e)}"
    
    def _comando_buscar_agentes_por_tipo(self, params: Dict[str, Any]) -> str:
        """
        Busca agentes TESS por tipo específico
        
        Args:
            params: Parâmetros com tipo de agente
            
        Returns:
            Resposta formatada com os agentes encontrados
        """
        # Extrair o tipo do parâmetro
        tipo = params.get('tipo', '').strip().lower()
        if not tipo:
            return "❌ Por favor, especifique o tipo de agente (chat, text, etc)."
            
        # Chamar o método de busca com o tipo apenas
        return self._comando_buscar_agentes({'tipo': tipo})
    
    def _comando_buscar_agentes_por_tipo_e_termo(self, params: Dict[str, Any]) -> str:
        """
        Busca agentes TESS por tipo e termo
        
        Args:
            params: Parâmetros com tipo de agente e termo de busca
            
        Returns:
            Resposta formatada com os agentes encontrados
        """
        # Extrair o tipo e o termo dos parâmetros
        tipo = params.get('tipo', '').strip().lower()
        termo = params.get('termo', '').strip()
        
        if not tipo:
            return "❌ Por favor, especifique o tipo de agente (chat, text, etc)."
            
        if not termo:
            return "❌ Por favor, especifique um termo para buscar agentes do tipo especificado."
            
        # Chamar o método de busca com tipo e termo
        return self._comando_buscar_agentes({'tipo': tipo, 'termo': termo})
    
    def _comando_executar_agente_tess(self, agent_id: str, mensagem: str, params: Dict[str, Any] = None, is_url: bool = False) -> str:
        """
        Executa um agente TESS com base em seu ID

        Args:
            agent_id: ID do agente a ser executado
            mensagem: Mensagem a ser processada
            params: Parâmetros específicos do agente obtidos da URL
            is_url: Indica se os parâmetros vieram de uma URL

        Returns:
            Resposta do agente ou mensagem de erro
        """
        if not TEST_API_TESS_AVAILABLE:
            return "Não foi possível acessar a API TESS. Verifique se o módulo 'test_api_tess.py' está disponível."
            
        try:
            # Configurar parâmetros específicos se for uma URL
            specific_params = None
            if is_url and params:
                specific_params = {
                    "temperature": params.get("temperature", "0.5"),
                    "model": params.get("model", "tess-5-pro"),
                    "tools": params.get("tools", "no-tools"),
                    "messages": [
                        {"role": "user", "content": mensagem or "Olá, como posso ajudar?"}
                    ],
                    "waitExecution": True
                }
                
                logging.info(f"Executando agente TESS a partir de URL com parâmetros: {specific_params}")
                
            # Executar o agente
            from tests.test_api_tess import executar_agente
            success, data = executar_agente(agent_id, mensagem, is_cli=False, specific_params=specific_params)
            
            if success and "output" in data:
                return data["output"]
            else:
                error_msg = data.get('error', 'Erro desconhecido')
                return f"Erro ao executar agente TESS: {error_msg}"
                
        except Exception as e:
            logging.error(f"Erro ao executar agente TESS: {e}")
            return f"Erro ao executar agente TESS: {str(e)}"
            
    def _comando_transformar_post_linkedin(self, params: Dict[str, Any]) -> str:
        """
        Transforma um texto em um post para LinkedIn usando o agente TESS específico
        Também oferece a opção de abrir a interface web do TESS
        
        Args:
            params: Parâmetros com o texto a ser transformado
            
        Returns:
            Resposta formatada com o post gerado e opção de interface web
        """
        # Verificar se temos o texto
        texto = params.get('texto', '').strip()
        if not texto:
            return "❌ Por favor, forneça o texto que deseja transformar em post para LinkedIn. Exemplo: 'Transformar em post para LinkedIn: Lançamos nosso novo produto de IA hoje.'"
        
        # ID do agente
        agent_id = 'transformar-texto-em-post-para-linkedin-mF37hV'
        
        # Oferecer a opção de usar a interface web
        dashboard_url = TESS_DASHBOARD_URLS.get(agent_id)
        web_option = ""
        if dashboard_url:
            web_option = f"\n\n💻 **Prefere usar a interface web?**\nDigite 'abrir tess linkedin' para acessar o gerador diretamente no navegador."
            
            # Se o comando específico para abrir a web for detectado
            if params.get('open_web'):
                try:
                    webbrowser.open(dashboard_url)
                    return f"✅ Abrindo interface web do TESS para transformar texto em post LinkedIn...\nURL: {dashboard_url}"
                except Exception as e:
                    logger.exception(f"Erro ao abrir navegador: {e}")
                    return f"❌ Não foi possível abrir o navegador. URL: {dashboard_url}"
        
        # Se não solicitou para abrir a web, executa o agente
        resultado = self._comando_executar_agente_tess(agent_id, texto, params, params.get('is_url', False))
        
        # Adicionar opção de interface web à resposta
        if resultado and web_option:
            resultado += web_option
            
        return resultado
    
    def _comando_criar_email_venda(self, params: Dict[str, Any]) -> str:
        """
        Cria um email de venda usando o agente TESS específico
        Também oferece a opção de abrir a interface web do TESS
        
        Args:
            params: Parâmetros com o produto/serviço
            
        Returns:
            Resposta formatada com o email gerado e opção de interface web
        """
        # Verificar se temos o produto/serviço
        produto = params.get('produto', '').strip()
        if not produto:
            return "❌ Por favor, especifique o produto ou serviço para o email de venda. Exemplo: 'Criar email de venda para: Software de automação de marketing'"
        
        # ID do agente
        agent_id = 'e-mail-de-venda-Sxtjz8'
        
        # Oferecer a opção de usar a interface web
        dashboard_url = TESS_DASHBOARD_URLS.get(agent_id)
        web_option = ""
        if dashboard_url:
            web_option = f"\n\n💻 **Prefere usar a interface web?**\nDigite 'abrir tess email' para acessar o gerador de email diretamente no navegador."
            
            # Se o comando específico para abrir a web for detectado
            if params.get('open_web'):
                try:
                    webbrowser.open(dashboard_url)
                    return f"✅ Abrindo interface web do TESS para criar email de venda...\nURL: {dashboard_url}"
                except Exception as e:
                    logger.exception(f"Erro ao abrir navegador: {e}")
                    return f"❌ Não foi possível abrir o navegador. URL: {dashboard_url}"
        
        # Se não solicitou para abrir a web, executa o agente
        resultado = self._comando_executar_agente_tess(agent_id, produto, params, params.get('is_url', False))
        
        # Adicionar opção de interface web à resposta
        if resultado and web_option:
            resultado += web_option
            
        return resultado
    
    def _comando_gerar_titulo_email(self, params: Dict[str, Any]) -> str:
        """
        Gera um título de email para anúncio de novo recurso
        
        Args:
            params: Parâmetros com o recurso anunciado
            
        Returns:
            Resposta formatada com o título gerado
        """
        # Verificar se temos o recurso
        recurso = params.get('recurso', '').strip()
        if not recurso:
            return "❌ Por favor, especifique o recurso ou produto para o título do email. Exemplo: 'Gerar título de email para anúncio: Nova interface do usuário'"
        
        # Prepara parâmetros para executar o agente apropriado
        return self._comando_executar_agente_tess('titulo-de-email-para-anuncio-de-novo-recurso-fDba8a', recurso, params, params.get('is_url', False))
    
    def _comando_mostrar_ajuda(self, params: Dict[str, Any]) -> str:
        """
        Mostra ajuda sobre os comandos disponíveis
        
        Args:
            params: Parâmetros (não utilizados)
            
        Returns:
            Mensagem de ajuda formatada
        """
        ajuda = """# Comandos TESS AI disponíveis

## Agentes e Templates
- **buscar agentes tess para <termo>** - Busca agentes por tema (email, linkedin, etc.)
- **buscar agentes tipo chat** - Busca agentes do tipo chat
- **buscar agentes tipo chat para <termo>** - Busca agentes do tipo chat com filtro adicional
- **listar agentes do tess** - Mostra todos os agentes disponíveis
- **listar agentes chat** - Mostra apenas os agentes do tipo chat
- **executar agente tess <id> com mensagem <texto>** - Executa um agente específico

## Comandos diretos
- **transformar texto em post para linkedin: <texto>** - Cria um post otimizado para LinkedIn
- **criar email de venda para: <produto>** - Gera um email persuasivo de vendas

## Interface Web
- **abrir tess linkedin** - Abre a interface web do TESS para criar posts do LinkedIn
- **abrir tess email** - Abre a interface web do TESS para criar emails de venda

## Testes API TESS
- **testar api tess para listar agentes** - Lista todos os agentes via API direta
- **testar api tess para listar agentes chat** - Lista agentes de chat via API direta
- **testar api tess <id> com mensagem <texto>** - Executa um agente específico via API direta
- **test_api_tess listar** - Versão abreviada para listar agentes
- **test_api_tess chat** - Versão abreviada para listar agentes chat
- **test_api_tess executar <id> <mensagem>** - Versão abreviada para executar agente

Use linguagem natural para interagir com os comandos. Experimente!"""
        
        return ajuda
    
    def _comando_listar_todos_agentes(self, params: Dict[str, Any]) -> str:
        """
        Lista todos os agentes disponíveis na TESS, com opção de filtrar por tipo
        
        Args:
            params: Parâmetros com filtro de tipo (opcional)
            
        Returns:
            Resposta formatada com os agentes
        """
        try:
            # Verificar se há filtro de tipo
            tipo_filtro = params.get('tipo', '').strip().lower()
            
            # Obter a chave de API do ambiente
            api_key = os.getenv("TESS_API_KEY")
            if not api_key:
                return "❌ ERRO: Chave API do TESS não encontrada nas variáveis de ambiente. Configure a variável TESS_API_KEY."
            
            # Configuração da requisição
            url = 'https://tess.pareto.io/api/agents'
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Parâmetros de paginação e filtro
            request_params = {
                'page': 1,
                'per_page': 30  # Aumentamos para ter mais resultados
            }
            
            # Adicionar filtro de tipo na requisição, se fornecido
            if tipo_filtro:
                request_params['type'] = tipo_filtro
                logging.info(f'Realizando requisição para listar agentes TESS com filtro de tipo: {tipo_filtro}...')
            else:
                logging.info('Realizando requisição para listar todos os agentes TESS...')
            
            # Fazer a requisição
            response = requests.get(url, headers=headers, params=request_params, timeout=30)
            response.raise_for_status()  # Levanta exceção para erros HTTP
            
            # Processar a resposta
            data = response.json()
            agentes = data.get('data', [])
            total = data.get('total', 0)
            
            # Filtrar localmente pelo tipo, se filtro não foi aplicado na requisição
            if tipo_filtro and 'type' not in request_params:
                agentes = [a for a in agentes if a.get('type', '').lower() == tipo_filtro]
                total = len(agentes)
            
            # Formatar a resposta
            if not agentes:
                if tipo_filtro:
                    return f"🔍 Nenhum agente do tipo '{tipo_filtro}' disponível no momento."
                else:
                    return "🔍 Nenhum agente disponível no momento."
            
            # Texto do cabeçalho com base no filtro
            if tipo_filtro:
                resposta = f"📋 Lista de agentes do tipo '{tipo_filtro}' (Total: {total}):\n\n"
            else:
                resposta = f"📋 Lista de agentes disponíveis (Total: {total}):\n\n"
            
            for i, agente in enumerate(agentes, 1):
                # Obter o tipo do agente (chat, text, etc)
                tipo_agente = agente.get('type', 'desconhecido')
                tipo_icone = "💬" if tipo_agente == "chat" else "📝" if tipo_agente == "text" else "🔄"
                
                resposta += f"{i}. {agente.get('title', 'Sem título')} {tipo_icone}\n"
                resposta += f"   ID: {agente.get('id', 'N/A')}\n"
                resposta += f"   Slug: {agente.get('slug', 'N/A')}\n"
                resposta += f"   Tipo: {tipo_agente.capitalize()}\n"
                resposta += f"   Descrição: {agente.get('description', 'Sem descrição')}\n\n"
            
            resposta += "Para executar um agente, use: executar agente <slug> \"sua mensagem aqui\""
            
            return resposta
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao listar agentes TESS: {e}")
            return f"❌ Erro ao listar agentes: {str(e)}"
    
    def _comando_buscar_ajuda(self, params: Dict[str, Any]) -> str:
        """
        Responde a perguntas sobre como fazer algo com o TESS
        
        Args:
            params: Parâmetros com ação desejada
            
        Returns:
            Resposta com instruções
        """
        acao = params.get('acao', '').lower()
        
        # Mapear ações comuns para respostas específicas
        if 'post' in acao or 'linkedin' in acao:
            return "Para criar um post para LinkedIn, você pode usar:\n\n'transformar texto em post para linkedin: seu texto aqui'\n\nOu então: 'executar agente tess transformar-texto-em-post-para-linkedin-mF37hV com mensagem seu texto aqui'"
        
        elif 'email' in acao or 'e-mail' in acao or 'venda' in acao:
            return "Para criar um email de vendas, você pode usar:\n\n'criar email de venda para: nome do seu produto/serviço'\n\nOu então: 'executar agente tess e-mail-de-venda-Sxtjz8 com mensagem descrição do seu produto/serviço'"
        
        elif 'título' in acao or 'assunto' in acao or 'anúncio' in acao:
            return "Para criar um título ou assunto de email para anúncio, você pode usar:\n\n'gerar título de email para anúncio: nome do recurso ou produto'\n\nOu então: 'executar agente tess titulo-de-email-para-anuncio-de-novo-recurso-fDba8a com mensagem nome do recurso'"
        
        elif 'agentes' in acao or 'modelos' in acao or 'templates' in acao:
            return "Para ver todos os agentes disponíveis, digite:\n\n'listar agentes do tess'\n\nPara buscar agentes sobre um tema específico:\n'buscar agentes tess para: tema de interesse'"
        
        # Resposta genérica
        return "Se você quer utilizar o TESS, veja as opções disponíveis com 'mostrar comandos' ou tente um destes formatos:\n\n1. 'transformar texto em post para linkedin: seu texto'\n2. 'criar email de venda para: seu produto'\n3. 'buscar agentes tess para: tema de interesse'"
    
    # Novos métodos para testar a API TESS
    
    def _comando_testar_api_listar_agentes(self, params: Dict[str, Any]) -> str:
        """
        Testa a API do TESS para listar todos os agentes
        
        Args:
            params: Parâmetros (opcional - pode conter filtros)
            
        Returns:
            Resposta formatada com a lista de agentes
        """
        from tests.test_api_tess import listar_agentes
        
        # Verificar se há filtro de tipo nos parâmetros
        filter_type = params.get('tipo') if params else None
        
        # Chamar a função importada com parâmetro is_cli=False para retornar os dados
        sucesso, dados = listar_agentes(is_cli=False, filter_type=filter_type)
        
        if not sucesso:
            return f"❌ Erro ao testar API TESS: {dados.get('error', 'Erro desconhecido')}"
        
        # Formatar a resposta para exibição
        total_agentes = len(dados.get('data', []))
        tipo_msg = f" do tipo '{filter_type}'" if filter_type else ""
        resposta = [f"✅ API do TESS testada com sucesso! Total de agentes{tipo_msg}: {total_agentes}\n"]
        
        # Adicionar informações de cada agente
        for i, agente in enumerate(dados.get('data', []), 1):
            resposta.append(f"{i}. {agente.get('title', 'Sem título')}")
            resposta.append(f"   ID: {agente.get('id', 'N/A')}")
            resposta.append(f"   Slug: {agente.get('slug', 'N/A')}")
            resposta.append(f"   Tipo: {agente.get('type', 'N/A')}")
            resposta.append("")
        
        return "\n".join(resposta)
        
    def _comando_testar_api_executar_agente(self, params: Dict[str, Any]) -> str:
        """
        Testa a API do TESS para executar um agente específico
        
        Args:
            params: Parâmetros com ID do agente e mensagem
            
        Returns:
            Resposta formatada com o resultado da execução
        """
        # Obter ID do agente
        agente_id = params.get('id', '').strip()
        if not agente_id:
            return "❌ Por favor, especifique o ID do agente TESS para testar."
        
        # Obter mensagem
        mensagem = params.get('mensagem', '').strip()
        if not mensagem:
            return f"❌ Por favor, forneça uma mensagem para testar o agente '{agente_id}'."
        
        try:
            # Capturar a saída da função executar_agente
            old_stdout = sys.stdout
            new_stdout = io.StringIO()
            
            with redirect_stdout(new_stdout):
                success = executar_agente(agente_id, mensagem)
            
            output = new_stdout.getvalue()
            
            # Formatar a resposta para o chat
            if success:
                # Extrair o resultado da execução
                linhas = output.split('\n')
                resposta = f"✅ **Resultado da API TESS (executar agente {agente_id}):**\n\n"
                
                # Procurar pela resposta do agente
                found_response = False
                response_text = ""
                
                for i, linha in enumerate(linhas):
                    if 'Resposta do agente:' in linha and i+1 < len(linhas):
                        found_response = True
                        continue
                    
                    if found_response and not linha.startswith('Detalhes completos:'):
                        response_text += linha + "\n"
                    
                    if 'Detalhes completos:' in linha:
                        found_response = False
                
                if response_text:
                    resposta += response_text
                else:
                    resposta += f"A API foi executada com sucesso, mas não foi possível extrair a resposta do agente.\n\n```\n{output[:500]}...\n```"
                
                return resposta
            else:
                return f"❌ Falha ao executar agente via API TESS.\n\n```\n{output[:500]}...\n```"
                
        except Exception as e:
            logger.exception(f"Erro ao testar API TESS (executar agente): {e}")
            return f"❌ Erro ao testar API TESS: {str(e)}"
    
    def _comando_testar_api_tess(self, params: Dict[str, Any]) -> str:
        """
        Comando abreviado para testar API do TESS (listar ou executar)
        
        Args:
            params: Parâmetros com subcamando e possíveis argumentos
            
        Returns:
            Resultado do comando executado
        """
        # Verificar qual subcomando deve ser processado
        subcomando = params.get('id') if 'id' in params else None
        
        if not subcomando:
            # Se não tiver subcomando, verificar outros parâmetros
            for palavra in ['listar', 'executar', 'chat']:
                if palavra in str(params):
                    subcomando = palavra
                    break
        
        # Processar o subcomando
        if subcomando == 'listar':
            return self._comando_testar_api_listar_agentes({})
        elif subcomando == 'chat':
            return self._comando_testar_api_listar_agentes_chat({})
        elif subcomando in ['executar', 'exec'] and 'mensagem' in params:
            # Extrair ID do agente do primeiro parâmetro
            agente_id = params.get('id', '').split()[0] if params.get('id') else ''
            # Extrair mensagem do segundo parâmetro
            mensagem = params.get('mensagem', '')
            
            if not agente_id or not mensagem:
                return "❌ Comando incompleto: Forneça o ID do agente e a mensagem"
                
            return self._comando_testar_api_executar_agente({
                'id': agente_id,
                'mensagem': mensagem
            })
        else:
            return """⚠️ Comando test_api_tess requer um subcomando válido:
- test_api_tess listar = Lista todos os agentes
- test_api_tess chat = Lista agentes do tipo chat
- test_api_tess executar {ID} {MENSAGEM} = Executa um agente específico"""

    def _comando_executar_agente(self, params: Dict[str, Any]) -> str:
        """
        Executa um agente TESS com um ID e uma mensagem
        
        Args:
            params: Dicionário com 'agent_id' e 'mensagem'
            
        Returns:
            Resposta formatada com a saída do agente
        """
        # Verificar se o módulo test_api_tess está disponível
        if not TEST_API_TESS_AVAILABLE:
            return "❌ Módulo test_api_tess não está disponível. Verifique se o arquivo está no diretório 'tests'."
        
        # Obter agente_id e mensagem dos parâmetros
        agent_id = params.get('agent_id', '').strip()
        if not agent_id:
            return "❌ Por favor, especifique o ID ou slug do agente."
        
        mensagem = params.get('mensagem', '').strip()
        if not mensagem:
            return f"❌ Por favor, forneça uma mensagem para o agente '{agent_id}'."
        
        # Remover caracteres extras que possam ter vindo do LLM (como aspas)
        agent_id = agent_id.strip('"\'`')
        mensagem = mensagem.strip('"\'`')
        
        logger.info(f"Executando agente TESS (ID: {agent_id}) com mensagem: {mensagem[:50]}...")
        
        try:
            # Verificar o tipo de agente e configurar parâmetros específicos
            specific_params = None
            
            if agent_id == "ideias-de-anuncios-para-o-youtube-ads-RVm1a8" or agent_id == "68":
                specific_params = {
                    "temperature": "1",
                    "model": "tess-ai-light",
                    "maxlength": 750,
                    "language": "Portuguese (Brazil)",
                    "tema-do-anuncio": mensagem,
                    "area-de-atucao-da-empresa": "Educação e Treinamento",
                    "publico-alvo": "Profissionais buscando aprimoramento em marketing digital",
                    "ocasiao-especial": "Lançamento do curso",
                    "descreva-o-produto-ou-servico": "Curso completo de marketing digital com conteúdo prático",
                    "company-name": "Academia de Marketing Digital"
                }
                logger.info("Usando parâmetros específicos para o agente de anúncios do YouTube")
            
            # Usar a função do módulo test_api_tess com parâmetros específicos, se disponíveis
            if specific_params:
                success, response = executar_agente(agent_id, mensagem, is_cli=False, specific_params=specific_params)
            else:
                success, response = executar_agente(agent_id, mensagem, is_cli=False)
            
            if success:
                # Verificar se há output direto
                if "output" in response:
                    output_text = response["output"]
                    return f"✅ **Resposta do agente TESS ({agent_id}):**\n\n{output_text}"
                # Verificar se há resultado parcial
                elif "partial_result" in response:
                    partial = response["partial_result"]
                    if 'responses' in partial and len(partial['responses']) > 0:
                        response_data = partial['responses'][0]
                        status = response_data.get('status', 'desconhecido')
                        
                        # Se o status for 'failed', recuperar a mensagem de erro
                        if status == 'failed':
                            error_info = response_data.get('error', {})
                            error_message = error_info.get('message', 'Erro desconhecido')
                            return f"❌ Falha na execução do agente: {error_message}"
                        
                        # Se for 'succeeded' mas não temos output ainda
                        if status == 'succeeded':
                            output = response_data.get('output', 'Sem saída disponível')
                            return f"✅ **Resposta do agente TESS ({agent_id}):**\n\n{output}"
                        
                        return f"⏳ Execução do agente em andamento. Status: {status}"
                    
                    return "⏳ Execução do agente iniciada. Aguarde o processamento."
            else:
                error_msg = response.get("error", "Erro desconhecido")
                error_details = response.get("details", {})
                
                # Verificar se temos detalhes específicos do erro
                if isinstance(error_details, dict):
                    if "status" in error_details and error_details["status"] == 422:
                        error_text = error_details.get("text", "")
                        try:
                            error_json = json.loads(error_text)
                            if "message" in error_json:
                                error_message = error_json["message"]
                                error_fields = error_json.get("errors", {})
                                
                                # Listar campos obrigatórios faltantes
                                missing_fields = []
                                for field, msgs in error_fields.items():
                                    if msgs and "required" in msgs[0]:
                                        missing_fields.append(field)
                                
                                if missing_fields:
                                    return (f"❌ Erro 422: O agente '{agent_id}' exige campos obrigatórios que não foram fornecidos:\n"
                                           f"{', '.join(missing_fields)}\n"
                                           f"Por favor, forneça esses campos ou use um agente diferente.")
                                
                                return f"❌ Erro ao executar agente: {error_message}"
                        except:
                            pass
                    
                    return (f"❌ Erro 422: O agente '{agent_id}' rejeitou a requisição, provavelmente "
                           f"porque faltam parâmetros obrigatórios ou o formato está incorreto.\n"
                           f"Tente usar um agente diferente ou verificar se o formato dos parâmetros está correto.")
                
                if "text" in error_details:
                    try:
                        # Tentar extrair mensagem de erro mais detalhada
                        error_json = json.loads(error_details["text"])
                        if "message" in error_json:
                            return f"❌ Erro ao executar agente: {error_json['message']}"
                    except:
                        pass
                
                return f"❌ Erro ao executar agente: {error_msg} (Status: {error_details.get('status', 'Desconhecido')})"
            
            return f"❌ Erro ao executar agente: {error_msg}"
        except Exception as e:
            logger.exception(f"Erro ao executar agente: {e}")
            return f"❌ Erro ao executar agente: {str(e)}"

    def _comando_listar_agentes_chat(self, params: Dict[str, Any]) -> str:
        """
        Lista apenas os agentes do tipo 'chat' disponíveis na TESS
        
        Args:
            params: Parâmetros (não utilizados)
            
        Returns:
            Resposta formatada com os agentes de chat
        """
        # Chamar o método _comando_listar_todos_agentes com filtro de tipo 'chat'
        return self._comando_listar_todos_agentes({'tipo': 'chat'})

    def _comando_testar_api_listar_agentes_chat(self, params: Dict[str, Any]) -> str:
        """
        Testa a API do TESS para listar apenas os agentes do tipo 'chat'
        
        Args:
            params: Parâmetros (não utilizados)
            
        Returns:
            Resposta formatada com a lista de agentes de chat
        """
        # Chamar o método _comando_testar_api_listar_agentes com filtro de tipo 'chat'
        return self._comando_testar_api_listar_agentes({'tipo': 'chat'})

    def _comando_listar_agentes_por_keyword(self, params: Dict[str, Any]) -> str:
        """
        Lista agentes que contêm uma palavra-chave específica no título ou descrição
        
        Args:
            params: Parâmetros com a keyword a ser usada na busca
            
        Returns:
            Resposta formatada com os agentes encontrados
        """
        keyword = params.get("keyword", "").strip()
        
        if not keyword:
            return "❌ Erro: Palavra-chave não especificada. Por favor, forneça uma palavra-chave para a busca."
        
        try:
            if TEST_API_TESS_AVAILABLE:
                logger.info(f"Realizando requisição para listar agentes TESS com palavra-chave: {keyword}")
                
                # Chama a função listar_agentes com o parâmetro keyword
                success, data = listar_agentes(is_cli=False)
                
                if success and 'data' in data:
                    agentes = data.get('data', [])
                    
                    # Filtrar localmente por cada palavra-chave
                    keywords = [k.strip().lower() for k in keyword.split() if k.strip()]
                    agentes_filtrados = []
                    
                    for agente in agentes:
                        title = agente.get('title', '').lower()
                        description = agente.get('description', '').lower()
                        slug = agente.get('slug', '').lower()
                        tipo = agente.get('type', '').lower()
                        
                        # Verificar se todas as palavras-chave estão presentes
                        if all(k in title or k in description or k in slug or k in tipo for k in keywords):
                            agentes_filtrados.append(agente)
                    
                    total = len(agentes_filtrados)
                    
                    if total > 0:
                        # Limitar para evitar respostas muito longas
                        max_display = 30
                        display_count = min(total, max_display)
                        
                        resposta = f"📋 Lista de agentes contendo '{keyword}' (Total: {total}):\n\n"
                        
                        for i, agent in enumerate(agentes_filtrados[:display_count], 1):
                            title = agent.get('title', 'Sem título')
                            id_num = agent.get('id', 'N/A')
                            slug = agent.get('slug', 'N/A')
                            tipo_agente = agent.get('type', 'N/A')
                            descricao = agent.get('description', 'Sem descrição')
                            
                            # Adicionar emoji para agentes de chat para facilitar a identificação
                            emoji = "💬" if tipo_agente.lower() == "chat" else "📝" if tipo_agente.lower() == "text" else "🔄"
                            
                            resposta += f"{i}. {title} {emoji}\n"
                            resposta += f"   ID: {id_num}\n"
                            resposta += f"   Slug: {slug}\n"
                            resposta += f"   Tipo: {tipo_agente.capitalize()}\n"
                            resposta += f"   Descrição: {descricao}\n\n"
                        
                        if total > max_display:
                            resposta += f"... e mais {total - max_display} agentes não exibidos.\n\n"
                        
                        resposta += "Para executar um agente, use: executar agente <slug> \"sua mensagem aqui\""
                        return resposta
                    else:
                        return f"❌ Nenhum agente encontrado com as palavras-chave '{keyword}'."
                else:
                    error_msg = data.get("error", "Erro desconhecido")
                    return f"❌ Erro ao listar agentes: {error_msg}"
            else:
                return "❌ Erro: Módulo test_api_tess não disponível. Não é possível listar agentes."
        except Exception as e:
            logger.exception(f"Erro ao listar agentes por keyword: {e}")
            return f"❌ Erro ao listar agentes: {str(e)}"
    
    def _comando_listar_agentes_por_tipo_e_keyword(self, params: Dict[str, Any]) -> str:
        """
        Lista agentes de um tipo específico que contêm uma palavra-chave no título ou descrição
        
        Args:
            params: Parâmetros com o tipo e a keyword para a busca
            
        Returns:
            Resposta formatada com os agentes encontrados
        """
        tipo = params.get("tipo", "").strip().lower()
        keyword = params.get("keyword", "").strip()
        
        if not tipo:
            return "❌ Erro: Tipo de agente não especificado. Por favor, forneça um tipo (chat, text, completion)."
        
        if not keyword:
            return "❌ Erro: Palavra-chave não especificada. Por favor, forneça uma palavra-chave para a busca."
        
        try:
            if TEST_API_TESS_AVAILABLE:
                logger.info(f"Realizando requisição para listar agentes TESS do tipo '{tipo}' com palavra-chave: {keyword}")
                
                # Chama a função listar_agentes com os parâmetros filter_type
                success, data = listar_agentes(is_cli=False, filter_type=tipo)
                
                if success and 'data' in data:
                    agentes = data.get('data', [])
                    
                    # Filtrar localmente por cada palavra-chave
                    keywords = [k.strip().lower() for k in keyword.split() if k.strip()]
                    agentes_filtrados = []
                    
                    for agente in agentes:
                        title = agente.get('title', '').lower()
                        description = agente.get('description', '').lower()
                        slug = agente.get('slug', '').lower()
                        
                        # Verificar se todas as palavras-chave estão presentes
                        if all(k in title or k in description or k in slug for k in keywords):
                            agentes_filtrados.append(agente)
                    
                    total = len(agentes_filtrados)
                    
                    if total > 0:
                        # Limitar para evitar respostas muito longas
                        max_display = 30
                        display_count = min(total, max_display)
                        
                        resposta = f"📋 Lista de agentes do tipo '{tipo}' contendo '{keyword}' (Total: {total}):\n\n"
                        
                        for i, agent in enumerate(agentes_filtrados[:display_count], 1):
                            title = agent.get('title', 'Sem título')
                            id_num = agent.get('id', 'N/A')
                            slug = agent.get('slug', 'N/A')
                            tipo_agente = agent.get('type', 'N/A')
                            descricao = agent.get('description', 'Sem descrição')
                            
                            # Adicionar emoji para agentes de chat para facilitar a identificação
                            emoji = "💬" if tipo_agente.lower() == "chat" else "📝" if tipo_agente.lower() == "text" else "🔄"
                            
                            resposta += f"{i}. {title} {emoji}\n"
                            resposta += f"   ID: {id_num}\n"
                            resposta += f"   Slug: {slug}\n"
                            resposta += f"   Tipo: {tipo_agente.capitalize()}\n"
                            resposta += f"   Descrição: {descricao}\n\n"
                        
                        if total > max_display:
                            resposta += f"... e mais {total - max_display} agentes não exibidos.\n\n"
                        
                        resposta += "Para executar um agente, use: executar agente <slug> \"sua mensagem aqui\""
                        return resposta
                    else:
                        return f"❌ Nenhum agente do tipo '{tipo}' encontrado com as palavras-chave '{keyword}'."
                else:
                    error_msg = data.get("error", "Erro desconhecido")
                    return f"❌ Erro ao listar agentes: {error_msg}"
            else:
                return "❌ Erro: Módulo test_api_tess não disponível. Não é possível listar agentes."
        except Exception as e:
            logger.exception(f"Erro ao listar agentes por tipo e keyword: {e}")
            return f"❌ Erro ao listar agentes: {str(e)}" 