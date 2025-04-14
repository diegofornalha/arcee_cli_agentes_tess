# Documentação da Pasta `examples`

## Visão Geral

A pasta `examples` no projeto `arcee_cli_agentes_tess` contém exemplos de código, scripts de demonstração e casos de uso para ilustrar como utilizar os diferentes componentes e funcionalidades do sistema. Esta pasta serve como recurso educacional para desenvolvedores que desejam entender como integrar e utilizar a API TESS, o protocolo MCP (Model Context Protocol) e outros recursos da plataforma.

## Estrutura da Pasta

A pasta `examples` está organizada da seguinte maneira:

1. `__init__.py` (6 linhas) - Arquivo de inicialização do pacote com descrição básica
2. `mcp/` (subpasta) - Exemplos específicos para integração com o MCP (Model Context Protocol)

### Subpasta `mcp/`

A subpasta `mcp/` contém diversos exemplos relacionados à integração com o protocolo MCP:

1. `demo_mcpx.py` (282 linhas) - Demonstração completa do cliente MCPX simplificado
2. `teste_tess.py` (116 linhas) - Testes para a integração da API TESS com MCP.run
3. `mcp_sse_app.py` (97 linhas) - Aplicação cliente SSE para MCP.run
4. `mcp_sse_background.py` (178 linhas) - Cliente SSE para execução em background
5. `mcp_sse_background_subprocess.py` (121 linhas) - Versão alternativa com subprocessos
6. `temp_tess_agents.py` (27 linhas) - Script temporário para teste de agentes TESS
7. `sample_server.py` (7 linhas) - Servidor de exemplo minimalista
8. `instalar_servico.sh` (87 linhas) - Script para instalação do serviço MCP
9. `.env.example` (13 linhas) - Modelo de arquivo de variáveis de ambiente
10. `.env` (20 linhas) - Arquivo de configuração com variáveis de ambiente
11. `mcp_sse_service.service` (19 linhas) - Definição de serviço para systemd
12. `com.arcee.mcp-sse-client.plist` (30 linhas) - Arquivo de configuração para launchd (macOS)
13. `agno/` (subpasta) - Exemplos específicos para integração direta com TESS

#### Subpasta `mcp/agno/`

A subpasta `agno/` dentro de `mcp/` contém exemplos específicos para interação direta com a API TESS:

1. `tess_example.py` (1 linha) - Arquivo de exemplo minimalista
2. `tess_test.sh` (39 linhas) - Script de shell para testar a API TESS
3. `tess_teste_direto.sh` (41 linhas) - Script para testes diretos sem MCP

## Funcionalidades Demonstradas

A pasta `examples` demonstra várias funcionalidades importantes:

### 1. Integração com MCP.run

Os exemplos mostram como:
- Gerar e gerenciar sessões MCP
- Listar ferramentas disponíveis
- Executar ferramentas específicas
- Processar resultados de ferramentas

### 2. Comunicação com API TESS

Os scripts demonstram:
- Listagem de agentes TESS
- Execução de agentes
- Listagem de arquivos
- Verificação de autenticação

### 3. Processamento de Eventos em Tempo Real

Os exemplos de SSE (Server-Sent Events) mostram:
- Conexão com endpoints SSE
- Processamento de eventos em tempo real
- Execução como serviço de background
- Configuração como serviço do sistema

### 4. Configuração e Instalação

Os scripts de configuração demonstram:
- Configuração de variáveis de ambiente
- Instalação como serviço do sistema
- Configuração para inicialização automática

## Importância no Projeto

A pasta `examples` desempenha várias funções importantes:

1. **Documentação Viva**: Demonstra o uso real das funcionalidades do sistema
2. **Testes Manuais**: Fornece scripts para testar componentes individualmente
3. **Aprendizado**: Ajuda novos desenvolvedores a entender a integração entre sistemas
4. **Protótipos**: Contém implementações de referência que podem ser adaptadas
5. **Depuração**: Oferece ferramentas simples para diagnóstico de problemas

## Casos de Uso

### Caso de Uso 1: Teste Rápido de Integração MCP-TESS

O arquivo `teste_tess.py` permite verificar rapidamente se a integração entre MCP.run e API TESS está funcionando corretamente, testando:
- Disponibilidade das ferramentas MCP
- Listagem de agentes TESS
- Listagem de arquivos TESS

### Caso de Uso 2: Cliente MCP Simplificado

O arquivo `demo_mcpx.py` implementa um cliente simplificado para MCP.run que pode ser usado como base para:
- Geração de novas sessões
- Listagem de ferramentas disponíveis
- Execução de ferramentas com parâmetros personalizados

### Caso de Uso 3: Monitoramento de Eventos

Os scripts `mcp_sse_app.py` e `mcp_sse_background.py` demonstram como monitorar eventos do MCP.run em tempo real, seja:
- De forma interativa com feedback no console
- Como serviço de background com registro em log

## Estado Atual e Recomendações

### Estado Atual

A pasta `examples` contém uma boa variedade de exemplos cobrindo as principais funcionalidades do sistema, mas:
- Alguns exemplos poderiam beneficiar-se de mais comentários e documentação inline
- A organização poderia ser melhorada para agrupar exemplos relacionados
- Alguns exemplos parecem ser protótipos ou scripts temporários (como `temp_tess_agents.py`)

### Recomendações para Melhoria

1. **Documentação**: Adicionar um README em cada subpasta explicando os exemplos contidos
2. **Organização**: Agrupar exemplos por funcionalidade (básicos, avançados, serviços)
3. **Limpeza**: Remover ou refatorar scripts temporários ou obsoletos
4. **Tutoriais**: Transformar exemplos em tutoriais passo a passo
5. **Consistência**: Padronizar o estilo de código e estrutura entre exemplos

## Conclusão

A pasta `examples` é um componente valioso do projeto, fornecendo exemplos práticos e funcionais que ilustram como usar os diferentes componentes da plataforma. Ela serve tanto como documentação prática quanto como recurso de aprendizado para desenvolvedores. Embora existam oportunidades para melhorar a organização e documentação dos exemplos, eles já oferecem um bom ponto de partida para compreender e trabalhar com o sistema. 