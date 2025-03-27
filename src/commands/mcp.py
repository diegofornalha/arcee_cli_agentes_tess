#!/usr/bin/env python
"""
Comandos para interação com o MCP (Module Command Processor).
"""

import os
import sys
import json
import logging
import click
from rich import print
from rich.console import Console
from rich.table import Table
from typing import Optional, Dict, Any, List
from ..utils.logging import get_logger
from pathlib import Path

# Configuração de logger
logger = get_logger(__name__)
console = Console()

# Tente importar o MCPRunClient simplificado
try:
    from ..tools.mcpx_simple import MCPRunClient, configure_mcprun
    MCPRUN_SIMPLE_AVAILABLE = True
    logger.info("Módulo MCPRunClient simplificado disponível")
except ImportError:
    MCPRUN_SIMPLE_AVAILABLE = False
    logger.warning("Módulo MCPRunClient simplificado não disponível")

# Variável global para armazenar o ID da sessão MCP
_mcp_session_id = None


def get_mcp_session_id() -> Optional[str]:
    """Obtém o ID da sessão MCP salvo."""
    global _mcp_session_id
    
    if _mcp_session_id:
        return _mcp_session_id
        
    # Tenta carregar da configuração
    config_file = os.path.expanduser("~/.arcee/config.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                _mcp_session_id = config.get("mcp_session_id")
                if _mcp_session_id:
                    return _mcp_session_id
        except Exception as e:
            logger.error(f"Erro ao carregar ID de sessão MCP: {e}")
    
    return None


def save_mcp_session_id(session_id: str) -> bool:
    """Salva o ID da sessão MCP na configuração."""
    global _mcp_session_id
    _mcp_session_id = session_id
    
    # Cria o diretório .arcee se não existir
    config_dir = os.path.expanduser("~/.arcee")
    config_file = os.path.join(config_dir, "config.json")
    
    try:
        os.makedirs(config_dir, exist_ok=True)
        
        # Carrega configuração existente se houver
        config = {}
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
        
        # Atualiza com o novo ID de sessão
        config["mcp_session_id"] = session_id
        
        # Salva a configuração
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
            
        logger.info(f"ID de sessão MCP salvo: {session_id}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar ID de sessão MCP: {e}")
        return False


def configurar_mcp(session_id: Optional[str] = None) -> None:
    """Configura o cliente MCP.run com um ID de sessão."""
    if not MCPRUN_SIMPLE_AVAILABLE:
        print("❌ Módulo MCP.run não está disponível")
        print("💡 Verifique a instalação do pacote simplificado")
        return
    
    try:
        print("🔄 Configurando MCP.run...")
        
        # Usar o configure_mcprun para obter um ID de sessão
        new_session_id = configure_mcprun(session_id)
        
        if new_session_id:
            # Salvar o ID de sessão para uso futuro
            if save_mcp_session_id(new_session_id):
                print(f"✅ ID de sessão MCP configurado: {new_session_id}")
                
                # Testar a conexão listando ferramentas
                client = MCPRunClient(session_id=new_session_id)
                tools = client.get_tools()
                print(f"ℹ️ Encontradas {len(tools)} ferramentas disponíveis")
            else:
                print("⚠️ Configuração salva, mas houve erro ao persistir")
                print(f"ID de sessão atual: {new_session_id}")
        else:
            print("❌ Não foi possível configurar o MCP.run")
            print("💡 Verifique os logs para mais detalhes")
    except Exception as e:
        logger.exception(f"Erro ao configurar MCP.run: {e}")
        print(f"❌ Erro ao configurar MCP.run: {e}")


def listar_ferramentas() -> None:
    """Lista as ferramentas disponíveis no MCP."""
    if not MCPRUN_SIMPLE_AVAILABLE:
        print("❌ Módulo MCP.run não está disponível")
        print("💡 Verifique a instalação do pacote simplificado")
        return
    
    session_id = get_mcp_session_id()
    if not session_id:
        print("❌ MCP não configurado. Execute primeiro: arcee mcp configurar")
        return
    
    print("🔍 Obtendo lista de ferramentas disponíveis...")
    try:
        client = MCPRunClient(session_id=session_id)
        tools = client.get_tools()
        
        if not tools:
            print("ℹ️ Nenhuma ferramenta MCP.run disponível")
            return
            
        # Cria a tabela
        tabela = Table(title="🔌 Ferramentas MCP.run")
        tabela.add_column("Nome", style="cyan")
        tabela.add_column("Descrição", style="green")
        
        # Adiciona as ferramentas à tabela
        for tool in tools:
            tabela.add_row(tool["name"], tool["description"])
            
        # Exibe a tabela
        console.print(tabela)
        
    except Exception as e:
        logger.exception(f"Erro ao listar ferramentas MCP: {e}")
        print(f"❌ Erro ao listar ferramentas MCP: {e}")


def executar_ferramenta(nome: str, params_json: Optional[str] = None) -> None:
    """Executa uma ferramenta MCP específica com os parâmetros fornecidos."""
    if not MCPRUN_SIMPLE_AVAILABLE:
        print("❌ Módulo MCP.run não está disponível")
        print("💡 Verifique a instalação do pacote simplificado")
        return
    
    session_id = get_mcp_session_id()
    if not session_id:
        print("❌ MCP não configurado. Execute primeiro: arcee mcp configurar")
        return
    
    # Processa os parâmetros
    try:
        params = {}
        if params_json:
            params = json.loads(params_json)
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON: {e}")
        print(f"❌ Erro nos parâmetros JSON: {e}")
        return
    
    # Executa a ferramenta
    print(f"🚀 Executando ferramenta '{nome}'...")
    try:
        client = MCPRunClient(session_id=session_id)
        result = client.run_tool(nome, params)
        
        if result.get("error"):
            print(f"❌ Erro ao executar ferramenta: {result['error']}")
            if result.get("raw_output"):
                print("Saída original:")
                print(result["raw_output"])
        else:
            print("✅ Resultado:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
    except Exception as e:
        logger.exception(f"Erro ao executar ferramenta: {e}")
        print(f"❌ Erro ao executar ferramenta: {e}")


# Função para implementar o MCPRunClient simplificado se não estiver disponível
def create_mcpx_simple_module():
    """Cria o módulo mcpx_simple.py se não existir."""
    tools_dir = Path(__file__).parent.parent / "tools"
    tools_dir.mkdir(exist_ok=True)
    
    # Cria o arquivo __init__.py no diretório tools se não existir
    init_file = tools_dir / "__init__.py"
    if not init_file.exists():
        with open(init_file, "w") as f:
            f.write("# Pacote de ferramentas para o CLI\n")
    
    # Caminho para o módulo mcpx_simple.py
    mcpx_file = tools_dir / "mcpx_simple.py"
    
    # Se o arquivo já existe, não faz nada
    if mcpx_file.exists():
        return
    
    # Conteúdo do módulo mcpx_simple.py
    mcpx_content = """#!/usr/bin/env python
\"\"\"
Cliente simplificado para o MCP.run.
\"\"\"

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class MCPRunClient:
    \"\"\"Cliente simplificado para o MCP.run.\"\"\"
    
    def __init__(self, session_id: Optional[str] = None):
        \"\"\"Inicializa o cliente com um ID de sessão.\"\"\"
        self.session_id = session_id or os.getenv("MCP_SESSION_ID")
        self.api_url = os.getenv("MCP_API_URL", "https://www.mcp.run/api")
        
        if not self.session_id:
            raise ValueError("Session ID não fornecido e MCP_SESSION_ID não configurado")
    
    def get_tools(self) -> List[Dict[str, Any]]:
        \"\"\"Obtém a lista de ferramentas disponíveis.\"\"\"
        try:
            headers = {"Content-Type": "application/json"}
            url = f"{self.api_url}/mcp/get-tools?session_id={self.session_id}"
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if "results" in result and "tools" in result["results"]:
                return result["results"]["tools"]
            return []
        except Exception as e:
            logger.error(f"Erro ao obter ferramentas: {e}")
            return []
    
    def run_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Executa uma ferramenta com os parâmetros fornecidos.\"\"\"
        try:
            headers = {"Content-Type": "application/json"}
            url = f"{self.api_url}/mcp/tool-call"
            
            data = {
                "session_id": self.session_id,
                "tool": tool_name,
                "method": "call",  # Método padrão
                "parameters": params
            }
            
            response = requests.post(
                url, 
                headers=headers, 
                json=data,
                timeout=60
            )
            
            if response.status_code != 200:
                return {
                    "error": f"Erro HTTP {response.status_code}",
                    "raw_output": response.text
                }
            
            return response.json()
        except Exception as e:
            logger.exception(f"Erro ao executar ferramenta {tool_name}: {e}")
            return {"error": str(e)}

def configure_mcprun(session_id: Optional[str] = None) -> Optional[str]:
    \"\"\"
    Configura o cliente MCP.run.
    
    Se um session_id for fornecido, ele será usado.
    Caso contrário, tenta usar o da variável de ambiente.
    
    Returns:
        str: ID de sessão configurado ou None se falhar
    \"\"\"
    try:
        # Se foi fornecido um ID de sessão, usá-lo
        if session_id:
            return session_id
            
        # Se não fornecido, tenta usar o da variável de ambiente
        env_session_id = os.getenv("MCP_SESSION_ID")
        if env_session_id:
            # Testa se a sessão é válida
            client = MCPRunClient(session_id=env_session_id)
            try:
                tools = client.get_tools()
                if tools is not None:  # Mesmo que vazio, é válido
                    return env_session_id
            except:
                # Se der erro, a sessão pode estar expirada
                pass
                
        # Se chegou aqui, não temos uma sessão válida
        print("⚠️ Nenhuma sessão MCP válida encontrada")
        print("💡 Especifique o ID de sessão ou configure a variável MCP_SESSION_ID")
        
        # No futuro, poderíamos implementar um fluxo de login
        # Por enquanto, retorna None
        return None
    except Exception as e:
        logger.exception(f"Erro ao configurar MCP.run: {e}")
        return None
"""
    
    # Escreve o conteúdo no arquivo
    with open(mcpx_file, "w") as f:
        f.write(mcpx_content)
    
    print("✅ Módulo mcpx_simple.py criado em src/tools/")
    print("💡 Agora você pode importar MCPRunClient deste módulo")


# Funções de comando para o CLI
def main_configurar(session_id: Optional[str] = None) -> None:
    """Função de comando para configurar o MCP."""
    if not MCPRUN_SIMPLE_AVAILABLE:
        create_mcpx_simple_module()
        print("⚠️ Módulo MCPRunClient criado, mas precisa ser importado")
        print("💡 Reinicie a aplicação para usar as funcionalidades MCP")
        return
    
    configurar_mcp(session_id)


def main_listar() -> None:
    """Função de comando para listar ferramentas MCP."""
    if not MCPRUN_SIMPLE_AVAILABLE:
        create_mcpx_simple_module()
        print("⚠️ Módulo MCPRunClient criado, mas precisa ser importado")
        print("💡 Reinicie a aplicação para usar as funcionalidades MCP")
        return
    
    listar_ferramentas()


def main_executar(nome: str, params_json: Optional[str] = None) -> None:
    """Função de comando para executar uma ferramenta MCP."""
    if not MCPRUN_SIMPLE_AVAILABLE:
        create_mcpx_simple_module()
        print("⚠️ Módulo MCPRunClient criado, mas precisa ser importado")
        print("💡 Reinicie a aplicação para usar as funcionalidades MCP")
        return
    
    executar_ferramenta(nome, params_json) 