# Documentação da Pasta `src`

## Visão Geral

A pasta `src` constitui o núcleo de código-fonte do projeto Arcee CLI, sendo responsável pela implementação da interface de linha de comando (CLI) que permite a interação com a API TESS através do protocolo MCP. Esta pasta segue os princípios de arquitetura limpa (Clean Architecture) e organização modular, contendo comandos, provedores, ferramentas e utilitários necessários para o funcionamento do sistema.

## Propósito

O propósito principal desta pasta é:

1. **Implementar a CLI**: Fornecer uma interface de linha de comando robusta para interagir com os serviços TESS.
2. **Integrar com MCP**: Facilitar a comunicação com o protocolo MCP (Model Context Protocol).
3. **Abstrair Provedores**: Encapsular a lógica de comunicação com diferentes APIs (TESS, MCP).
4. **Fornecer Ferramentas**: Implementar utilitários e ferramentas para processamento de linguagem natural e comunicação.
5. **Organizar Comandos**: Estruturar os diferentes comandos disponíveis para o usuário final.

## Estrutura e Componentes

### Arquivos Principais

1. **`__init__.py`**: Define o módulo principal e expõe a aplicação CLI, exportando-a como `app`.
2. **`__main__.py`**: Implementa o ponto de entrada da aplicação CLI utilizando o framework Click, definindo os comandos principais como `chat`, `conversar` e o grupo de comandos `mcp`.

### Subdiretórios

#### 1. `/commands`

Contém a implementação dos comandos disponíveis na CLI.

- **`chat.py`**: Implementação do comando para chat interativo.
- **`mcp.py`**: Implementação dos comandos relacionados ao MCP (configurar, listar, executar).

Este diretório é responsável por definir a interface de usuário da CLI, interpretando os argumentos da linha de comando e direcionando para as ações apropriadas.

#### 2. `/providers`

Contém classes que encapsulam a comunicação com APIs externas.

- **`tess_provider.py`**: Implementa a classe `TessProvider` para interagir com a API TESS, incluindo operações como `health_check`, `list_agents`, `get_agent` e `execute_agent`.
- **`mcp_provider.py`**: Implementa a comunicação com o protocolo MCP, fornecendo métodos para configuração e execução de ferramentas MCP.

Estes provedores são fundamentais para isolar a lógica de comunicação com serviços externos, seguindo o princípio de inversão de dependência.

#### 3. `/tools`

Contém implementações de ferramentas específicas e utilitários especializados.

- **`mcpx_simple.py`**: Implementa o `MCPRunClient`, um cliente simplificado para interação com o MCP.run através do proxy TESS, permitindo listar e executar ferramentas MCP.
- **`mcp_nl_processor.py`**: Implementa processamento de linguagem natural para interpretar comandos em linguagem natural.

Estas ferramentas fornecem funcionalidades especializadas que são utilizadas pelos comandos e provedores para executar tarefas específicas.

#### 4. `/utils`

Contém utilitários compartilhados e funções auxiliares.

- **`logging.py`**: Implementa a configuração de logging para a aplicação, garantindo registro adequado de eventos e mensagens.

Estes utilitários oferecem funcionalidades de apoio usadas em diversos componentes da aplicação.

#### 5. `/services`

Um diretório destinado a implementações de serviços específicos, seguindo o padrão de camadas da arquitetura limpa, embora atualmente contenha apenas um diretório `__pycache__`.

## Fluxo de Execução Principal

O fluxo típico de execução através dos componentes da pasta `src` é:

1. O usuário executa um comando via CLI, que é interpretado por `__main__.py`.
2. O comando é redirecionado para o módulo apropriado em `/commands`.
3. O comando utiliza provedores de `/providers` para comunicar com serviços externos.
4. Os provedores podem utilizar ferramentas de `/tools` para tarefas específicas.
5. Utilitários de `/utils` são usados ao longo do processo para funções auxiliares.

## Recursos Principais

### Comandos CLI

A pasta implementa os seguintes comandos principais:

- **`chat` / `conversar`**: Inicia um chat interativo com o Arcee AI usando modo AUTO.
- **`mcp configurar`**: Configura a integração com MCP.run.
- **`mcp listar`**: Lista todas as ferramentas disponíveis no MCP.run.
- **`mcp executar`**: Executa uma ferramenta MCP.run específica.

### Funcionalidades Implementadas

Os componentes da pasta `src` implementam:

1. **Comunicação com TESS**: Capacidade de listar, obter detalhes e executar agentes TESS.
2. **Integração MCP**: Suporte completo para protocolo MCP, permitindo descobrir e executar ferramentas.
3. **Modo Local**: Suporte para execução com servidor local ou remoto (controlado por variáveis de ambiente).
4. **Fallback Inteligente**: Mecanismo de fallback entre diferentes provedores quando um falha.

## Padrões de Design Utilizados

1. **Command Pattern**: Implementado na estrutura de comandos CLI.
2. **Provider Pattern**: Utilizado para abstrair a comunicação com serviços externos.
3. **Dependency Injection**: Injeção de dependências entre os componentes.
4. **Factory Method**: Utilizado em alguns componentes para criar instâncias de objetos.

## Integração com o Projeto

A pasta `src` integra-se com o restante do projeto da seguinte forma:

1. É importada pelo script de entrada `arcee_cli.py` na raiz do projeto.
2. Utiliza componentes da pasta `infrastructure` para configuração e logging.
3. Integra-se com o servidor MCP-TESS para comunicação com serviços externos.
4. Depende das variáveis de ambiente definidas nos arquivos `.env`.

## Recomendações

1. **Testes Automatizados**: Implementar testes unitários e de integração para os componentes principais.
2. **Documentação de API**: Melhorar a documentação das interfaces públicas.
3. **Consistência de Estilo**: Manter consistência nos padrões de código e nomenclatura.
4. **Tratamento de Erros**: Implementar estratégias mais robustas para tratamento de erros.
5. **Type Hints**: Expandir o uso de type hints para melhorar a verificação estática de tipos.

## Conclusão

A pasta `src` é o coração do projeto Arcee CLI, implementando todos os componentes essenciais para a interface de linha de comando e a integração com os serviços TESS e MCP. Sua estrutura modular e bem organizada facilita a manutenção e a extensão, permitindo que o projeto evolua de maneira controlada e sustentável. 