# Integração do Arcee com MCP no Framework Agno

Este projeto demonstra como integrar o modelo Arcee com ferramentas MCP (Multi-Channel Processing) usando o framework Agno para criação de agentes inteligentes.

## Componentes da Solução

### 1. Modelo Arcee (arcee_model.py)

O arquivo `arcee_model.py` implementa a classe `ArceeModel` que herda de `agno.models.base.Model`. Esta classe:

- Estabelece a conexão com a API da Arcee
- Implementa métodos síncronos e assíncronos para invocar o modelo
- Suporta streaming de respostas
- Mantém estatísticas de uso dos modelos

### 2. Agente MCP (arcee_agno_mcp.py)

O script principal `arcee_agno_mcp.py` demonstra:

- Configuração do servidor MCP com `databutton-app-mcp`
- Gerenciamento do ciclo de vida do servidor MCP
- Integração com as ferramentas MCP através do `agno.tools.mcp.MCPTools`
- Construção de um agente usando o modelo Arcee e ferramentas MCP
- Processamento de mensagens em modo streaming e não-streaming

### 3. Script de Execução (run_arcee_mcp.sh)

O script `run_arcee_mcp.sh` facilita a execução do exemplo:

- Ativa o ambiente virtual
- Permite executar com ou sem argumentos de linha de comando

## Requisitos

- Python 3.8+
- Variáveis de ambiente configuradas (ARCEE_API_KEY, ARCEE_APP_URL, DATABUTTON_API_KEY)
- Pacotes instalados:
  - agno
  - mcp
  - databutton-app-mcp
  - openai (para interagir com a API Arcee)
  - httpx
  - dotenv

## Uso

Existem duas formas de utilizar este exemplo:

### 1. Modo interativo

```bash
./run_arcee_mcp.sh
```

### 2. Consulta única

```bash
./run_arcee_mcp.sh "Sua consulta aqui"
```

## Implementação do Servidor MCP

Um servidor MCP também foi implementado em `/home/agentsai/backend/direct_mcp_server.py`, que:

- Define ferramentas MCP para listar, criar e obter detalhes de agentes
- Utiliza um banco de dados em memória para armazenar os agentes
- Pode ser executado em uma porta específica (padrão: 8001)

## Fluxo de Comunicação

1. O usuário envia uma mensagem para o agente
2. O framework Agno processa a mensagem e a envia para o modelo Arcee
3. O modelo Arcee gera uma resposta que pode incluir chamadas de ferramentas
4. As ferramentas MCP executam as ações solicitadas
5. Os resultados são enviados de volta para o modelo Arcee para gerar a resposta final
6. A resposta é apresentada ao usuário

## Próximos Passos

- Integrar com mais ferramentas especializadas
- Implementar persistência para os agentes
- Criar interfaces de usuário para interagir com os agentes 