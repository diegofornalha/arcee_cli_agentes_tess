# Guia de Integração Técnica - TESS API

Este documento unifica as informações técnicas sobre como integrar a API TESS em diferentes contextos, incluindo MCP (Model Context Protocol) e a CLI Arcee.

## Índice

1. [Visão Geral da API TESS](#visão-geral-da-api-agno)
2. [Integração com MCP](#integração-com-mcp)
3. [Implementação do TESS Provider](#implementação-do-agno-provider)
4. [Integração do MCP na CLI TESS](#integração-do-mcp-na-cli-agno)
5. [Autenticação e Configuração](#autenticação-e-configuração)

---

## Visão Geral da API TESS

### Base URL e Autenticação

- **Base URL**: `https://api.agno.pareto.io/api`
- **Autenticação**: Token Bearer
- **Header**: `Authorization: Bearer YOUR_API_KEY`
- **Formato**: JSON (`Content-Type: application/json`)
- **Limite de Taxa**: 1 requisição por segundo (entre em contato com o suporte para aumentar)

### Obtenção do API Key

O API key pode ser obtido através de:
1. Dashboard: TESS AI → User Tokens
2. UI: Acessar TESS AI → Menu de Usuário → API Tokens → Add New Token

### Principais Endpoints

| Categoria | Endpoint | Método | Descrição |
|-----------|----------|--------|-----------|
| Agentes | /agents | GET | Listar todos os agentes |
| Agentes | /agents/{id} | GET | Obter um agente específico |
| Agentes | /agents/{id}/execute | POST | Executar um agente |
| Respostas | /agent-responses/{id} | GET | Obter resposta de execução |
| Arquivos de Agente | /agents/{agentId}/files | GET | Listar arquivos de agente |
| Arquivos de Agente | /agents/{agentId}/files | POST | Vincular arquivos ao agente |
| Arquivos de Agente | /agents/{agentId}/files/{fileId} | DELETE | Excluir arquivo de agente |
| Webhooks de Agente | /agents/{id}/webhooks | GET | Listar webhooks de agente |
| Webhooks de Agente | /agents/{id}/webhooks | POST | Criar webhook de agente |
| Arquivos | /files | GET | Listar todos os arquivos |
| Arquivos | /files | POST | Carregar um arquivo |
| Arquivos | /files/{fileId} | GET | Obter detalhes de arquivo |
| Arquivos | /files/{fileId} | DELETE | Excluir um arquivo |
| Arquivos | /files/{fileId}/process | POST | Processar um arquivo |
| Webhooks | /webhooks | GET | Listar todos os webhooks |
| Webhooks | /webhooks/{id} | DELETE | Excluir um webhook |

### Paginação

Controle de paginação com parâmetros:
- **page**: Número da página (padrão: 1, mínimo: 1)
- **per_page**: Itens por página (padrão: 15, mínimo: 1, máximo: 100)

---

## Integração com MCP

O Model Context Protocol (MCP) é uma interface padronizada para integração de modelos e ferramentas. A integração com a API TESS permite acesso às funcionalidades via MCP.

### Implementação do Servidor MCP-TESS

```typescript
// TypeScript (mcp-server-agno/src/index.ts)
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import axios from "axios";
import { z } from "zod";

// Inicializa o servidor MCP
const server = new McpServer({
  name: "TessAIConnector",
  version: "1.0.0",
});

// Configuração base para requisições à API da TESS
const TESS_API_BASE_URL = "https://agno.pareto.io/api";
const TESS_API_KEY = process.env.TESS_API_KEY;

// Configura o cliente HTTP com autenticação
const apiClient = axios.create({
  baseURL: TESS_API_BASE_URL,
  headers: {
    "Authorization": `Bearer ${TESS_API_KEY}`,
    "Content-Type": "application/json"
  }
});
```

### Ferramentas MCP para TESS

#### Listar Agentes

```typescript
server.tool(
  "listar_agentes_tess",
  {
    page: z.number().optional().describe("Número da página (padrão: 1)"),
    per_page: z.number().optional().describe("Itens por página (padrão: 15, máx: 100)")
  },
  async ({ page = 1, per_page = 15 }: { page?: number; per_page?: number }) => {
    try {
      const response = await apiClient.get("/agents", {
        params: { page, per_page }
      });
      
      return {
        content: [{ 
          type: "text", 
          text: JSON.stringify(response.data) 
        }],
      };
    } catch (error) {
      console.error("Erro ao listar agentes:", error);
      return {
        content: [{ 
          type: "text", 
          text: JSON.stringify({ error: "Falha ao listar agentes" }) 
        }],
      };
    }
  }
);
```

#### Executar um Agente

```typescript
server.tool(
  "executar_agente_tess",
  {
    agent_id: z.string().describe("ID do agente a ser executado"),
    temperature: z.string().optional().describe("Temperatura para geração (0-1)"),
    model: z.string().optional().describe("Modelo a ser usado"),
    messages: z.array(z.object({
      role: z.string(),
      content: z.string()
    })).describe("Mensagens para o agente (formato chat)"),
    tools: z.string().optional().describe("Ferramentas a serem habilitadas"),
    file_ids: z.array(z.number()).optional().describe("IDs dos arquivos a serem anexados"),
    waitExecution: z.boolean().optional().describe("Esperar pela execução completa")
  },
  async ({ 
    agent_id, 
    temperature = "0.5", 
    model = "agno-ai-light", 
    messages, 
    tools = "no-tools", 
    file_ids = [], 
    waitExecution = false 
  }) => {
    try {
      const payload = {
        temperature,
        model,
        messages,
        tools,
        waitExecution,
        file_ids
      };
      
      const response = await apiClient.post(`/agents/${agent_id}/execute`, payload);
      
      return {
        content: [{ 
          type: "text", 
          text: JSON.stringify(response.data) 
        }],
      };
    } catch (error) {
      console.error(`Erro ao executar agente ${agent_id}:`, error);
      return {
        content: [{ 
          type: "text", 
          text: JSON.stringify({ error: `Falha ao executar agente ${agent_id}` }) 
        }],
      };
    }
  }
);
```

### Inicialização do Servidor MCP

```typescript
// Configuração dos transportes
const stdinTransport = new StdioServerTransport();
server.addTransport(stdinTransport);

// Iniciar o servidor MCP
server.start().catch((err) => {
  console.error("Erro ao iniciar o servidor MCP:", err);
  process.exit(1);
});
```

---

## Implementação do TESS Provider

A classe `TessProvider` implementa a comunicação com a API TESS de forma encapsulada.

### Estrutura da Classe

```python
class TessProvider:
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None)
    def health_check(self) -> Tuple[bool, str]
    def list_agents(self, page: int = 1, per_page: int = 15) -> List[Dict]
    def get_agent(self, agent_id: str) -> Optional[Dict]
    def execute_agent(self, agent_id: str, params: Dict[str, Any], messages: List[Dict[str, str]]) -> Dict
```

### Inicialização

```python
def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
    """Inicializa o provedor TESS com a API key do ambiente."""
    self.api_key = api_key or os.getenv("TESS_API_KEY")
    self.api_url = api_url or os.getenv("TESS_API_URL", "https://agno.pareto.io/api")
    self.local_server_url = os.getenv("TESS_LOCAL_SERVER_URL", "http://localhost:3000")
    self.use_local_server = os.getenv("USE_LOCAL_TESS", "False").lower() in ("true", "1", "t")
    
    # Verificar se temos API key
    if not self.api_key and not self.use_local_server:
        raise ValueError("TESS API Key não encontrada. Configure a variável de ambiente TESS_API_KEY.")
    
    # Configurar headers com autenticação
    self.headers = {
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json"
    }
```

### Método List Agents

```python
def list_agents(self, page: int = 1, per_page: int = 15) -> List[Dict]:
    """
    Lista todos os agentes disponíveis na API TESS.
    
    Args:
        page: Número da página (padrão: 1)
        per_page: Número de itens por página (padrão: 15)
        
    Returns:
        Lista de dicionários com informações dos agentes
    """
    try:
        if self.use_local_server:
            # Simulação para servidor local
            return [
                {"id": "1", "title": "Agente Local 1", "description": "Simulação de agente"},
                {"id": "2", "title": "Agente Local 2", "description": "Outro agente simulado"}
            ]
        
        # Configurar parâmetros de paginação
        params = {
            "page": page,
            "per_page": per_page
        }
        
        # Fazer a requisição
        response = requests.get(f"{self.api_url}/agents", headers=self.headers, params=params)
        response.raise_for_status()
        
        # Extrair dados da resposta
        data = response.json()
        return data.get("data", [])
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao listar agentes: {e}")
        return []
```

### Método Execute Agent

```python
def execute_agent(self, agent_id: str, params: Dict[str, Any], messages: List[Dict[str, str]]) -> Dict:
    """
    Executa um agente TESS com os parâmetros e mensagens fornecidos.
    
    Args:
        agent_id: ID do agente a ser executado
        params: Dicionário com parâmetros para o agente
        messages: Lista de mensagens no formato [{role: str, content: str}]
        
    Returns:
        Dicionário com a resposta do agente
    """
    try:
        if self.use_local_server:
            # Simulação para servidor local
            return {
                "content": f"Resposta simulada do agente {agent_id}",
                "role": "assistant",
                "agent_id": agent_id
            }
        
        # Construir payload
        payload = {
            "inputs": params,
            "messages": messages
        }
        
        # Fazer a requisição
        response = requests.post(
            f"{self.api_url}/agents/{agent_id}/completions", 
            headers=self.headers, 
            json=payload
        )
        response.raise_for_status()
        
        # Extrair resposta
        data = response.json()
        return {
            "content": data.get("completion", ""),
            "role": "assistant",
            "agent_id": agent_id
        }
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao executar agente {agent_id}: {e}")
        if hasattr(e, 'response') and e.response:
            try:
                error_data = e.response.json()
                return {"error": error_data.get("message", str(e))}
            except:
                pass
        return {"error": str(e)}
```

---

## Integração do MCP na CLI TESS

### Arquitetura da Integração

A integração do MCP com a CLI TESS foi implementada com os seguintes componentes:

1. **Cliente MCP Simplificado**: Um cliente leve para fazer chamadas à API MCP.run
2. **Provedor MCP**: Gerencia credenciais e configurações do MCP
3. **Comandos CLI**: Interface de linha de comando para interagir com o MCP
4. **Processador de Linguagem Natural**: Permite executar comandos MCP diretamente do chat

### Arquivos Principais

```
arcee_cli/
├── src/
│   ├── commands/
│   │   └── mcp.py           # Comandos CLI do MCP
│   ├── providers/
│   │   └── mcp_provider.py  # Provedor para gerenciar credenciais
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── mcpx_simple.py   # Cliente simplificado MCP.run
│   │   └── mcp_nl_processor.py  # Processador para comandos no chat
│   └── __main__.py          # Integração com a CLI principal
```

### Variáveis de Ambiente

A integração MCP suporta as seguintes variáveis de ambiente:

- `MCP_SESSION_ID`: ID de sessão do MCP.run (opcional se configurado pelo CLI)
- `MCP_API_URL`: URL da API MCP.run (opcional, padrão: https://www.mcp.run/api)

### Arquivo de Configuração

As configurações do MCP são armazenadas no arquivo `~/.agno/mcp_config.json` com o seguinte formato:

```json
{
  "session_id": "seu-id-de-sessao-mcp"
}
```

### Comandos de Configuração

```python
@mcp_group.command("configurar")
@click.option('--session-id', help='ID de sessão MCP')
def mcp_configurar(session_id: str):
    """Configura o MCP com um ID de sessão."""
    main_configurar_mcp(session_id)
```

### Comandos de Execução

```python
@mcp_group.command("executar")
@click.argument('tool_name', required=True)
@click.option('--params', help='Parâmetros em formato JSON')
def mcp_executar(tool_name: str, params: Optional[str] = None):
    """Executa uma ferramenta MCP."""
    params_dict = {}
    if params:
        try:
            params_dict = json.loads(params)
        except json.JSONDecodeError:
            print("Erro: O formato JSON dos parâmetros é inválido.")
            return
    
    main_executar_ferramenta_mcp(tool_name, params_dict)
```

### Cliente MCP Simplificado

```python
class MCPRunClient:
    def __init__(self, session_id: str, api_url: str = "https://www.mcp.run/api"):
        self.session_id = session_id
        self.api_url = api_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {session_id}"
        }
    
    def list_tools(self) -> List[Dict]:
        """Lista todas as ferramentas disponíveis."""
        try:
            response = requests.get(f"{self.api_url}/tools", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Erro ao listar ferramentas MCP: {e}")
            return []
    
    def run_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict:
        """Executa uma ferramenta com os parâmetros especificados."""
        try:
            payload = {
                "tool": tool_name,
                "inputs": params
            }
            response = requests.post(f"{self.api_url}/run", headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Erro ao executar ferramenta MCP '{tool_name}': {e}")
            if hasattr(e, 'response') and e.response:
                try:
                    return e.response.json()
                except:
                    pass
            return {"error": str(e)}
```

---

## Autenticação e Configuração

### Configuração de Variáveis de Ambiente

```bash
# Configuração da API TESS
export TESS_API_KEY="sua-chave-api-agno"
export TESS_API_URL="https://agno.pareto.io/api"

# Configuração do MCP
export MCP_SESSION_ID="seu-id-de-sessao-mcp"
export MCP_API_URL="https://www.mcp.run/api"

# Configuração do servidor local (opcional)
export USE_LOCAL_TESS="False"
export TESS_LOCAL_SERVER_URL="http://localhost:3000"
```

### Armazenamento de Credenciais

```python
def save_config(session_id: str):
    """Salva o ID de sessão MCP no arquivo de configuração."""
    config_dir = os.path.expanduser("~/.agno")
    os.makedirs(config_dir, exist_ok=True)
    
    config_file = os.path.join(config_dir, "mcp_config.json")
    with open(config_file, 'w') as f:
        json.dump({"session_id": session_id}, f)
    
    print(f"Configuração MCP salva em {config_file}")
```

```python
def load_config() -> Optional[str]:
    """Carrega o ID de sessão MCP do arquivo de configuração."""
    config_file = os.path.expanduser("~/.agno/mcp_config.json")
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get("session_id")
        except (json.JSONDecodeError, IOError):
            pass
    
    return None
```

### Validação de Autenticação

```python
def validate_session(client: MCPRunClient) -> bool:
    """Valida se o ID de sessão é válido."""
    try:
        # Tenta listar ferramentas para verificar autenticação
        tools = client.list_tools()
        return isinstance(tools, list)
    except Exception:
        return False
```

## Fluxo de Uso Recomendado

1. **Configuração Inicial**:
   ```bash
   python -m src mcp configurar --session-id=seu-id-de-sessao
   ```

2. **Verificação de Ferramentas Disponíveis**:
   ```bash
   python -m src mcp listar
   ```

3. **Execução de Ferramentas**:
   ```bash
   python -m src mcp executar nome-da-ferramenta --params='{"param1": "valor1"}'
   ```

4. **Uso no Chat**:
   ```
   Abra o chat: arcee chat
   Configure MCP: configurar mcp com sessão abc123
   Liste ferramentas: listar ferramentas mcp
   Execute ferramenta: executar ferramenta nome-da-ferramenta com parâmetros {"param1": "valor1"}
   ```

## Benefícios da Integração

1. **Acesso Padronizado**: Interface consistente para acessar recursos através do MCP
2. **Segurança**: Tokens de API gerenciados adequadamente
3. **Composabilidade**: Capacidades podem ser combinadas com outras ferramentas
4. **Controle de Fluxo**: Gerenciamento centralizado de requisições e tratamento de erros
5. **Flexibilidade**: Suporte a servidor local para desenvolvimento e testes 