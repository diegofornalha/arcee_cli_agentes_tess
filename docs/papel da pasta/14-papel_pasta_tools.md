# Documentação da Pasta `tools`

## Visão Geral

A pasta `tools` contém um conjunto de utilidades e ferramentas que complementam a funcionalidade principal do projeto Arcee CLI, focando na integração com o protocolo MCP (Model Context Protocol) e no processamento de linguagem natural. Essas ferramentas são essenciais para a interação com serviços externos e a execução de tarefas especializadas que não estão diretamente relacionadas à interface de linha de comando principal.

## Propósito

O propósito principal desta pasta é:

1. **Integração com MCP**: Fornecer clientes e wrappers para interação com o protocolo MCP (Model Context Protocol).
2. **Processamento de Linguagem Natural**: Implementar ferramentas para interpretação e processamento de comandos em linguagem natural.
3. **Diagnóstico**: Oferecer utilidades para verificação de dependências e diagnóstico do ambiente de execução.
4. **Extensibilidade**: Disponibilizar componentes que podem ser utilizados por outras partes do sistema, como a pasta `src`.

## Componentes Principais

### 1. `mcpx_simple.py`

Implementa uma integração simplificada com o protocolo MCP.run, oferecendo:

- **Classe `MCPRunClient`**: Cliente que permite listar e executar ferramentas MCP.
- **Função `run_command_with_timeout`**: Executa comandos shell com timeout usando threads.
- **Configuração Flexível**: Suporte para configuração via IDs de sessão e variáveis de ambiente.

Este componente é fundamental para a comunicação com servidores MCP, permitindo descobrir e executar ferramentas remotas de forma estruturada e segura.

### 2. `mcpx_tools.py`

Fornece um wrapper para integrar ferramentas MCP.run com frameworks como CrewAI:

- **Classe `MCPTool`**: Wrapper que adapta ferramentas MCP para uso com CrewAI.
- **Função `get_mcprun_tools`**: Cria ferramentas CrewAI a partir das ferramentas MCP.run instaladas.
- **Conversão de Schemas**: Converte schemas JSON em modelos Pydantic para validação de dados.

Este módulo permite utilizar as ferramentas MCP em contextos mais amplos, como fluxos de trabalho automatizados e orquestração de agentes.

### 3. `tess_nl_processor.py`

Implementa processamento de linguagem natural específico para interação com TESS:

- **Análise de Comandos**: Interpreta comandos em linguagem natural para encontrar padrões e intenções.
- **Extração de Parâmetros**: Identifica parâmetros e argumentos em texto livre.
- **Detecção de Intenções**: Classifica comandos em diferentes tipos de intenções (executar agente, listar, etc.).

Este componente é essencial para permitir uma interface mais natural com o usuário, traduzindo frases em linguagem natural para comandos estruturados.

### 4. `check_deps.py`

Utilitário para verificar dependências e diagnosticar problemas com a instalação:

- **Verificação de Pacotes**: Detecta se pacotes Python necessários estão instalados.
- **Teste de Importações**: Tenta importar módulos específicos para validar a instalação.
- **Diagnóstico de Ambiente**: Verifica variáveis de ambiente e caminhos Python.

Esta ferramenta é valiosa para diagnosticar problemas de instalação e dependências, especialmente em ambientes novos ou quando ocorrem erros inesperados.

### 5. Pasta `mcp/`

Contém implementações específicas para o protocolo MCP:

- **Subpasta `tess/`**: Contém implementações específicas para integração do TESS com MCP.

Esta organização permite separar componentes por sua função específica, facilitando a manutenção e evolução do código.

## Fluxo de Uso Típico

O fluxo típico de uso das ferramentas nesta pasta envolve:

1. Verificação do ambiente com `check_deps.py` para garantir que todas as dependências estão instaladas.
2. Inicialização de um cliente MCP via `mcpx_simple.py` para se conectar a serviços MCP.
3. Descoberta e execução de ferramentas MCP usando `MCPRunClient`.
4. Processamento de comandos em linguagem natural com `tess_nl_processor.py`.
5. Integração com sistemas de automação via `mcpx_tools.py`.

## Integrações e Dependências

Estas ferramentas dependem de e integram-se com:

1. **MCP.run**: API e protocolo para Model Context Protocol.
2. **CrewAI**: Framework para orquestração de agentes (integração opcional).
3. **Serviços TESS**: API e serviços para processamento de texto e semântica.
4. **Bibliotecas Padrão**: Utilização de `subprocess`, `threading`, `json` para operações de baixo nível.

## Estado Atual e Recomendações

O estado atual das ferramentas é funcional, mas há oportunidades de melhoria:

1. **Documentação Interna**: Melhorar a documentação de funções e métodos com exemplos.
2. **Testes Automatizados**: Implementar testes unitários e de integração para as ferramentas.
3. **Tratamento de Erros**: Aprimorar o tratamento de erros e exceções para maior robustez.
4. **Configuração Centralizada**: Centralizar a configuração de parâmetros comuns.

## Relação com Outras Pastas

A pasta `tools` relaciona-se com outras partes do projeto da seguinte forma:

1. **`src/`**: As ferramentas são utilizadas pelos componentes principais na pasta `src`.
2. **`infrastructure/`**: Compartilha conceitos e componentes com a infraestrutura, embora com foco mais especializado.
3. **`tests/`**: As ferramentas são testadas pelos scripts na pasta `tests`.

## Conclusão

A pasta `tools` fornece componentes essenciais para estender a funcionalidade do Arcee CLI, permitindo a integração com o protocolo MCP e o processamento de linguagem natural. Estas ferramentas complementam a interface de linha de comando principal, oferecendo capacidades avançadas de interação com serviços externos e processamento de comandos em linguagem natural.

Juntas, essas ferramentas formam um ecossistema de utilidades que aumentam significativamente as capacidades do Arcee CLI, permitindo uma interface mais rica e natural para o usuário final. 