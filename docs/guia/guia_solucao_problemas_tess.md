# Guia de Solução de Problemas - TESS API e Arcee Chat

Este documento consolida todas as soluções para problemas comuns encontrados na integração entre o Arcee Chat e a API TESS.

## Índice

1. [Problemas com Comandos TESS](#problemas-com-comandos-agno)
2. [Problemas de Configuração do Chat](#problemas-de-configuração-do-chat)
3. [Problemas com o Servidor TESS Local](#problemas-com-o-servidor-agno-local)
4. [Problemas com o Comando `arcee chat`](#problemas-com-o-comando-arcee-chat)

---

## Problemas com Comandos TESS

### Erro de Importação Circular

#### Sintoma
```
Erro ao importar MCPNLProcessor: cannot import name 'chat' from partially initialized module 'crew.arcee_chat'
```

#### Solução
Implementamos um sistema de importação em cascata com variáveis globais:

```python
# Variáveis globais no topo do módulo
listar_agentes = None
executar_agente = None
TEST_API_TESS_AVAILABLE = False
MCP_NL_PROCESSOR_AVAILABLE = False
MCPNLProcessor = None

# Função auxiliar de importação
def _import_mcp_nl_processor():
    global MCP_NL_PROCESSOR_AVAILABLE, MCPNLProcessor
    try:
        from src.tools.mcp_nl_processor import MCPNLProcessor as _MCPNLP
        MCPNLProcessor = _MCPNLP
        MCP_NL_PROCESSOR_AVAILABLE = True
        return True
    except ImportError:
        # Tratamento de erros...
        return False
```

### Erro de Escopo de Variáveis

#### Sintoma
```
Erro: cannot access local variable 'listar_agentes' where it is not associated with a value
```

#### Solução
Adicionamos verificação de disponibilidade e reimportação sob demanda:

```python
if listar_agentes is None or executar_agente is None:
    # Tentar importar novamente caso as funções não estejam disponíveis
    try:
        from tests.test_api_tess import listar_agentes as _listar_agentes, executar_agente as _executar_agente
        global listar_agentes, executar_agente
        listar_agentes = _listar_agentes
        executar_agente = _executar_agente
        logger.info("Funções da API TESS reimportadas com sucesso")
    except ImportError as e:
        logger.error(f"Erro ao reimportar funções da API TESS: {e}")
```

### Comando "não implementado"

#### Sintoma
```
Comando não implementado: executar_agente
```

#### Solução
1. Implementamos múltiplas camadas de detecção de comandos:
   - Detecção direta via regex
   - Processamento via MCPNLProcessor
   - Suporte legado para comandos com prefixo `test_api_tess`

2. Implementamos comandos diretos no chat para evitar dependência do processador:

```python
# Verificar comandos diretos para TESS
if TEST_API_TESS_AVAILABLE:
    # Comando "listar agentes"
    if user_input.lower() in ["listar agentes", "listar os agentes", "mostrar agentes"]:
        logger.info("Detectado comando direto: listar_agentes")
        # Execução do comando
```

### Erro na Execução de Agentes

#### Sintoma
Erros 422 ou mensagens sobre parâmetros inválidos.

#### Solução
Implementamos consulta dinâmica à API e detecção automática de tipo de agente:

```python
# Se não é um ID numérico, vamos buscar na API
if not agent_id.isdigit():
    # Buscar de forma dinâmica na API
    try:
        success, data = listar_agentes(is_cli=False)
        if success:
            encontrado = False
            for agent in data.get('data', []):
                # Verificação de correspondência...
```

```python
# Verificar se é um agente de chat com base no tipo ou no ID
if ((tipo_agente and tipo_agente.lower() == "chat") or
    agent_id.lower().startswith("chat-") or 
    agent_id == "professional-dev-ai"):
    is_chat_agent = True
```

---

## Problemas de Configuração do Chat

### Erro com `return_model_info`

#### Sintoma
```
Erro na chamada à API da Arcee: Completions.create() got an unexpected keyword argument 'return_model_info'
```

#### Solução
Modificamos o código para remover o parâmetro não suportado:

```python
# Parâmetros adicionais para o modo auto
extra_params = {}
if self.model == "auto":
    # Pode incluir parâmetros específicos para o modo auto
    # como solicitação de metadados sobre o modelo selecionado
    extra_params = {}  # Antes era {"return_model_info": True}
    logger.info("Usando modo AUTO para seleção dinâmica de modelo")
```

### Erro com Módulo `tiktoken`

#### Sintoma
Erro indicando que o módulo `tiktoken` está faltando.

#### Solução
Instalamos o módulo corretamente:

```bash
pip install tiktoken --no-build-isolation
```

---

## Problemas com o Servidor TESS Local

### Diretório `arcee_cli.egg-info` Ausente

#### Sintoma
Erros relacionados à execução de scripts e localização de arquivos após remoção do diretório.

#### Solução
Reinstalamos o pacote em modo de desenvolvimento:

```bash
pip install -e . --no-deps
```

### Erro com a Biblioteca Extism

#### Sintoma
```
TypeError: Extism is not a constructor
```

#### Solução
Simplificamos o servidor TESS para usar um servidor HTTP básico:

```javascript
const http = require('http');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const port = process.env.PORT || 3000;

// Criar um servidor HTTP simples
const server = http.createServer((req, res) => {
    // Implementação simplificada
    // ...
});

server.listen(port, () => {
    console.log(`Servidor TESS iniciado na porta ${port}`);
});
```

### Script de Inicialização Problemático

#### Sintoma
Erros ao iniciar o servidor em segundo plano.

#### Solução
Modificamos o script `start_tess_server_background.sh`:

- Métodos mais confiáveis para determinar o diretório
- Detecção genérica do processo com `pgrep -f "node.*server.js"`
- Execução direta com `node server.js` em vez de `npm start`

---

## Problemas com o Comando `arcee chat`

### Erro de Pacote Não Encontrado

#### Sintoma
```
importlib.metadata.PackageNotFoundError: No package metadata was found for arcee-cli
```

#### Solução
Reinstalamos o pacote em modo de desenvolvimento:

```bash
python -m pip install -e . --no-deps
```

### Erro de Importação Relativa

#### Sintoma
```
ImportError: attempted relative import beyond top-level package
```

#### Solução
Corrigimos o import relativo no arquivo `src/commands/chat.py`:

```python
# Import problemático - tentando acessar níveis superiores além do pacote
from ...crew import arcee_chat

# Substituído por import absoluto correto
from crew.arcee_chat import chat as arcee_chat
```

E adicionamos os arquivos `__init__.py` nos diretórios necessários para garantir que sejam tratados como pacotes Python válidos:
- `src/commands/__init__.py` 
- `src/utils/__init__.py`

## Verificação de Soluções

Para verificar se as soluções estão funcionando corretamente:

1. **Para comandos TESS**:
   ```bash
   python run_arcee_chat.py
   ```
   Teste os comandos:
   ```
   listar agentes
   executar professional-dev-ai "Exemplo de código Python"
   ```

2. **Para o servidor local**:
   ```bash
   ./scripts/start_tess_server_background.sh
   curl http://localhost:3000/health
   ```

3. **Para o comando arcee**:
   ```bash
   arcee chat
   ```

## Práticas Recomendadas para Evitar Problemas

1. **Imports** - Prefira imports absolutos a relativos para evitar problemas de contexto.
2. **Variáveis** - Inicialize variáveis globais e use a palavra-chave `global` dentro de funções.
3. **Tratamento de erros** - Implemente tratamento de exceções abrangente para todas as operações críticas.
4. **Logging** - Mantenha logs detalhados para diagnóstico de problemas.
5. **Testes** - Adicione verificações de ambiente antes de executar comandos que dependem de configurações específicas. 