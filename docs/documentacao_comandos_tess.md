# Documentação Comandos TESS

Este documento unifica toda a documentação relacionada aos comandos TESS, incluindo comandos disponíveis, correções implementadas e soluções técnicas.

## Visão Geral

A integração com a API TESS permite executar diversos agentes de IA especializados diretamente do chat Arcee. Implementamos uma abordagem dinâmica que elimina a necessidade de manter listas estáticas de agentes no código, trazendo diversos benefícios:

1. **Dados sempre atualizados**: Consultas em tempo real garantem informações precisas
2. **Código mais limpo**: Eliminação de hardcoding de dados
3. **Manutenção simplificada**: Não é necessário atualizar o código quando novos agentes são adicionados
4. **Experiência do usuário melhorada**: Comandos mais intuitivos e diretos

## Comandos Disponíveis

### Comandos Simplificados (Recomendados)

Estes são os comandos mais simples e recomendados para uso no chat Arcee:

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `executar <id-do-agente> "<mensagem>"` | Executa um agente específico | `executar professional-dev-ai "Como implementar um singleton em Python?"` |
| `listar agentes` | Lista todos os agentes disponíveis | `listar agentes` |
| `listar agentes chat` | Lista apenas agentes do tipo chat | `listar agentes chat` |
| `agentes <palavra-chave>` | Busca agentes com uma palavra-chave | `agentes linkedin` |

### Comandos via Chat (Alternativos)

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `executar agente <id> com mensagem "<texto>"` | Executa um agente específico | `executar agente professional-dev-ai com mensagem "Como implementar um singleton em Python?"` |
| `buscar agentes agno para <termo>` | Busca agentes por tema | `buscar agentes agno para email` |
| `buscar agentes tipo chat para <termo>` | Busca agentes do tipo chat por tema | `buscar agentes tipo chat para linkedin` |
| `transformar texto em post para linkedin: <texto>` | Atalho para criar um post para LinkedIn | `transformar texto em post para linkedin: Lançamento do produto X` |
| `criar email de venda para: <produto>` | Atalho para gerar um email de vendas | `criar email de venda para: software de gestão` |

### Comandos via Linha de Comando

Estes comandos podem ser executados diretamente pelo terminal:

```bash
# Listar todos os agentes
python -m tests.test_api_tess listar

# Listar agentes de chat
python -m tests.test_api_tess listar-chat

# Listar agentes por palavra-chave
python -m tests.test_api_tess listar-keyword linkedin

# Executar um agente específico
python -m tests.test_api_tess executar professional-dev-ai "Como implementar um singleton em Python?"
```

## Implementação Técnica

### Consulta Dinâmica à API

A implementação utiliza consulta dinâmica à API TESS para identificar agentes:

1. **Consulta à API para identificação de agentes**:
   - Busca dinâmica por ID, slug ou título do agente
   - Suporte a correspondências parciais para maior flexibilidade

2. **Configuração automática com base no tipo**:
   - Detecta automaticamente se o agente é do tipo chat
   - Configura parâmetros adequados (modelo, temperatura) baseados no tipo

3. **Detecção de comandos simplificados**:
   - Suporte para sintaxe simplificada: `executar <id> "<mensagem>"`
   - Processamento via expressões regulares

### Correções Implementadas

As seguintes correções foram implementadas para resolver problemas comuns:

#### 1. Resolução de Importação Circular

```python
# Declaração de variáveis globais no início do módulo
listar_agentes = None
executar_agente = None
TEST_API_TESS_AVAILABLE = False
MCP_NL_PROCESSOR_AVAILABLE = False
MCPNLProcessor = None

# Função auxiliar de importação que evita a importação circular
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

#### 2. Verificação de Disponibilidade de Funções

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

## Solução de Problemas Comuns

### Erro "Comando não implementado"

Se você receber a mensagem "Comando não implementado", verifique:

1. Se está usando a sintaxe correta conforme este documento
2. Se o comando está entre os suportados
3. Se o módulo MCPNLProcessor foi carregado corretamente (verifique logs)

### Erro ao Executar Agentes

O erro `UnboundLocalError: cannot access local variable` foi resolvido com a inicialização correta das variáveis globais e escopo adequado.

### Erro de Chave API

Se receber erro relacionado à chave API não encontrada:

```bash
# Configure a variável de ambiente
export TESS_API_KEY="sua-chave-api-aqui"
```

### Agente Não Encontrado

Se um agente não for encontrado:

1. Verifique se o ID ou slug está correto usando o comando `listar agentes`
2. Confirme o acesso à API com sua chave
3. Tente usar o ID numérico se estiver usando slug

## Exemplos de Uso

### Exemplo 1: Encontrar um Agente para Posts de LinkedIn

```
agentes linkedin
```

### Exemplo 2: Executar um Agente de Chat

```
executar multi-chat-S7C0WU "Quais são as tendências de IA para 2023?"
```

### Exemplo 3: Criar Email de Vendas Rapidamente

```
criar email de venda para: software de gestão de projetos
```

## Observações Importantes

1. Certifique-se de que a variável de ambiente `TESS_API_KEY` esteja configurada
2. Os comandos via chat dependem da disponibilidade do servidor TESS
3. Para comandos de linha de comando, você deve estar no diretório raiz do projeto 