# Guia de Integração MCP na CLI TESS

Este documento explica como o suporte ao MCP (Module Command Processor) foi implementado na CLI TESS, permitindo usar ferramentas MCP.run diretamente do terminal ou do chat.

## O que é o MCP?

O MCP (Module Command Processor) é uma plataforma que permite acessar diversas ferramentas e integrações através de uma API unificada. Com o MCP.run, você pode:

- Acessar ferramentas como Gmail, Google Calendar, GitHub, etc.
- Executar ferramentas com parâmetros específicos
- Integrar facilmente novas ferramentas a aplicações existentes

## Arquitetura da Integração

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
└── docs/
    └── mcp-integracao.md    # Esta documentação
```

## Configuração

### Variáveis de Ambiente

A integração MCP suporta as seguintes variáveis de ambiente:

- `MCP_SESSION_ID`: ID de sessão do MCP.run (opcional se configurado pelo CLI)
- `MCP_API_URL`: URL da API MCP.run (opcional, padrão: https://www.mcp.run/api)

### Arquivo de Configuração

As configurações do MCP são armazenadas no arquivo `~/.tess/mcp_config.json` com o seguinte formato:

```json
{
  "session_id": "seu-id-de-sessao-mcp"
}
```

## Uso dos Comandos

### Via CLI

A CLI TESS oferece os seguintes comandos para interação com o MCP:

```bash
# Configurar o MCP.run com um ID de sessão
python -m src mcp configurar --session-id=seu-id-de-sessao

# Listar ferramentas disponíveis
python -m src mcp listar

# Executar uma ferramenta específica
python -m src mcp executar nome-da-ferramenta --params='{"param1": "valor1"}'
```

### Via Chat

Durante uma sessão de chat, você pode usar os seguintes comandos:

- **Configurar MCP**: `configurar mcp` ou `configurar mcp com sessão abc123`
- **Listar Ferramentas**: `listar ferramentas mcp` ou `mostrar tools mcp`
- **Executar Ferramenta**: `executar ferramenta nome-da-ferramenta` ou `executar ferramenta nome-da-ferramenta com parâmetros {"param1": "valor1"}`

## Implementação Técnica

### Cliente MCP Simplificado

O arquivo `src/tools/mcpx_simple.py` implementa um cliente leve para a API MCP.run com as seguintes funcionalidades:

- Autenticação com ID de sessão
- Listagem de ferramentas disponíveis
- Execução de ferramentas com parâmetros

### Provedor MCP

O arquivo `src/providers/mcp_provider.py` gerencia as credenciais do MCP com as seguintes funcionalidades:

- Leitura/gravação do ID de sessão no arquivo de configuração
- Recuperação do ID de sessão do ambiente ou do arquivo
- Funções para verificar e limpar configurações

### Processador de Linguagem Natural

O arquivo `src/tools/mcp_nl_processor.py` permite reconhecer comandos MCP em linguagem natural durante o chat:

- Detecção de comandos usando expressões regulares
- Execução de comandos MCP a partir do chat
- Formatação de respostas para apresentação ao usuário

## Estendendo a Integração

### Adicionando Novos Padrões de Comando

Para adicionar novos padrões de comando ao processador de linguagem natural, edite o arquivo `src/tools/mcp_nl_processor.py`:

```python
# Adicione novos padrões à lista comandos_padroes
self.comandos_padroes = [
    # Padrões existentes...
    (r'novo padrão de comando (?P<parametro>.*)', 'novo_tipo_comando'),
]

# Adicione o método correspondente
def _comando_novo_tipo_comando(self, params: Dict[str, Any]) -> str:
    # Implementação do comando
    return "Resultado do comando"
```

### Adicionando Novos Comandos CLI

Para adicionar novos comandos à CLI, edite o arquivo `src/commands/mcp.py`:

```python
# Adicione a função de comando
def novo_comando(parametro: str) -> None:
    """Implementação do novo comando."""
    # Código do comando
    
# Adicione a função principal para o CLI
def main_novo_comando(parametro: str) -> None:
    """Função de comando para o novo comando."""
    novo_comando(parametro)
```

Depois, atualize o arquivo `src/__main__.py` para registrar o novo comando:

```python
@mcp_group.command("novo-comando")
@click.argument("parametro", required=True)
def mcp_novo_comando(parametro: str):
    """Descrição do novo comando."""
    main_novo_comando(parametro)
```

## Limitações Atuais e Trabalhos Futuros

- **Processamento Avançado com LLM**: Atualmente, a detecção de comandos utiliza apenas expressões regulares. Uma melhoria futura seria integrar um modelo de linguagem para detecção mais flexível.
- **Cache de Respostas**: Implementar um sistema de cache para reduzir chamadas à API.
- **Interface Gráfica**: Desenvolver uma interface web para interação com ferramentas MCP.
- **Autenticação Avançada**: Implementar fluxo de autenticação completo para obter o ID de sessão automaticamente.

## Solução de Problemas

### MCP não configurado

Se você receber um erro indicando que o MCP não está configurado:

1. Execute `python -m src mcp configurar --session-id=seu-id-de-sessao`
2. Ou defina a variável de ambiente `MCP_SESSION_ID`
3. Verifique se o arquivo de configuração `~/.tess/mcp_config.json` existe e contém um ID de sessão válido

### Módulo MCPRunClient não disponível

Se o módulo MCPRunClient não estiver disponível:

1. Execute `python -m src mcp configurar` para criar o módulo automaticamente
2. Reinicie a aplicação para que as alterações sejam aplicadas

### Erro ao executar ferramenta

Se ocorrer um erro ao executar uma ferramenta:

1. Verifique se o ID de sessão é válido
2. Verifique se a ferramenta existe listando todas as ferramentas disponíveis
3. Verifique se os parâmetros fornecidos estão corretos

## Conclusão

A integração do MCP com a CLI TESS amplia significativamente as capacidades da ferramenta, permitindo acesso a diversas integrações externas diretamente do terminal ou do chat. O desenho modular da implementação facilita a manutenção e a adição de novas funcionalidades no futuro. 