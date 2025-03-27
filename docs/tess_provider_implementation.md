# Implementação do Provedor TESS

## Visão Geral

Este documento descreve a implementação do provedor TESS para integração com a API da Tess AI no projeto MCP-CLI-TESS, permitindo interações via linha de comando com agentes TESS.

## Configuração

### Variáveis de Ambiente

O provedor TESS requer as seguintes variáveis de ambiente:

```env
TESS_API_KEY=seu_token_aqui
TESS_API_URL=https://tess.pareto.io/api
```

## Estrutura do Código

### Classe TessProvider

A classe `TessProvider` foi implementada em `arcee_cli/infrastructure/providers/tess_provider.py` com os seguintes métodos:

```python
class TessProvider:
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None)
    def health_check(self) -> Tuple[bool, str]
    def list_agents(self, page: int = 1, per_page: int = 15) -> List[Dict]
    def get_agent(self, agent_id: str) -> Optional[Dict]
    def execute_agent(self, agent_id: str, params: Dict[str, Any], messages: List[Dict[str, str]]) -> Dict
```

### Funcionalidades Implementadas

1. **Inicialização**
   - Carrega configurações das variáveis de ambiente
   - Configura headers com autenticação Bearer token
   - Valida presença das configurações necessárias

2. **Health Check**
   - Verifica conexão com a API
   - Trata erros de autenticação e conexão
   - Retorna status e mensagem

3. **Listagem de Agentes**
   - Suporta paginação
   - Transforma resposta em formato amigável
   - Inclui ID, nome e descrição dos agentes

4. **Detalhes do Agente**
   - Obtém informações detalhadas de um agente
   - Inclui tipo, visibilidade e questões
   - Trata erros e retorna None em caso de falha

5. **Execução de Agentes**
   - Envia mensagens para o agente usando o endpoint `/agents/{id}/completions`
   - Processa resposta do agente e extrai o campo `completion`
   - Mantém histórico de conversas
   - Suporta envio de parâmetros configuráveis para cada agente

## Comandos CLI

O CLI inclui os seguintes comandos para interação com a API TESS:

### Listar Agentes

```bash
python -m arcee_cli tess listar-agentes
```

Opções:
- `--page`: Página de resultados (padrão: 1)
- `--per-page`: Itens por página (padrão: 15)

### Detalhes do Agente

```bash
python -m arcee_cli tess detalhes-agente <agent_id>
```

### Chat com Agente

```bash
python -m arcee_cli tess-chat <agent_id>
```

Opções:
- `--model`: Modelo a ser usado (padrão: tess-ai-light)
- `--language`: Idioma das respostas (padrão: Portuguese (Brazil))

## Integração com MCP

O provedor TESS está integrado ao sistema MCP (Multi-Cloud Protocol), permitindo:

1. Execução dos comandos através da CLI unificada
2. Compartilhamento de contexto entre diferentes provedores
3. Uso do sistema de logging padronizado
4. Gerenciamento centralizado de sessões

## Formato dos Dados

### Resposta da API de Listagem

```json
{
  "current_page": 1,
  "data": [
    {
      "id": 45,
      "title": "Nome do Agente",
      "description": "Descrição do Agente",
      // ...
    }
  ],
  "per_page": 15,
  "total": 613
}
```

### Resposta da API de Detalhes

```json
{
  "id": 45,
  "title": "Nome do Agente",
  "description": "Descrição do Agente",
  "type": "text",
  "visibility": "public",
  "questions": [
    {
      "type": "text",
      "name": "campo",
      "description": "Descrição do campo",
      "required": true
    }
  ]
}
```

### Formato da Requisição de Chat

```json
{
  "inputs": {
    "param1": "valor1",
    "param2": "valor2",
    "model": "tess-ai-light",
    "temperature": "0.7",
    "maxlength": 500,
    "language": "Portuguese (Brazil)"
  },
  "messages": [
    {"role": "user", "content": "Mensagem do usuário"},
    {"role": "assistant", "content": "Resposta do assistente"}
  ]
}
```

### Formato da Resposta de Chat

```json
{
  "completion": "Resposta do assistente",
  // outros campos da API
}
```

O provedor transforma esta resposta em:

```json
{
  "content": "Resposta do assistente",
  "role": "assistant",
  "agent_id": "45"
}
```

## Tratamento de Erros

O provedor implementa tratamento de erros para:
- Configurações ausentes
- Erros de autenticação (401)
- Erros de conexão
- Erros de requisição HTTP
- Dados inválidos ou ausentes
- Agentes não encontrados (404)

## Exemplo de Uso

### Usando o CLI

```bash
# Listar todos os agentes disponíveis
python -m arcee_cli tess listar-agentes

# Obter detalhes de um agente específico
python -m arcee_cli tess detalhes-agente 45

# Iniciar um chat com um agente
python -m arcee_cli tess-chat 45
```

### Usando a API Programaticamente

```python
from arcee_cli.infrastructure.providers.tess_provider import TessProvider

# Inicializar provedor
provider = TessProvider()

# Verificar conexão
status, message = provider.health_check()

# Listar agentes
agents = provider.list_agents(page=1, per_page=15)

# Obter detalhes de um agente
agent_details = provider.get_agent("45")

# Executar chat com agente
params = {
    "campo1": "valor1", 
    "campo2": "valor2",
    "model": "tess-ai-light",
    "temperature": "0.7"
}
messages = [{"role": "user", "content": "Olá, como posso te ajudar?"}]
response = provider.execute_agent("45", params, messages)
```

## Testes

Foram implementados scripts de teste para verificar a funcionalidade:

### Script de Teste do Provedor

```bash
python arcee_cli/test_tess.py
```

### Script de Teste da CLI

```bash
# Testar todas as funcionalidades
python test_tess_cli.py

# Testar chat com um agente específico
python test_tess_cli.py <agent_id>
```

## Interface Interativa

O comando `tess-chat` implementa uma interface interativa que:

1. Verifica conexão com a API
2. Exibe detalhes do agente selecionado
3. Solicita os parâmetros obrigatórios para o agente
4. Mantém o histórico da conversa
5. Permite sair digitando "sair"
6. Exibe mensagens com formatação colorida

## Próximos Passos

1. Melhorias na Interface:
   - Adicionar suporte a temas customizáveis
   - Implementar histórico persistente
   - Adicionar autocomplete para comandos e parâmetros

2. Funcionalidades Avançadas:
   - Exportação de conversas
   - Upload de arquivos para o contexto
   - Integração com outras ferramentas

3. Otimizações:
   - Cache de resultados
   - Configurações salvas para agentes frequentes
   - Execução em lote de comandos 