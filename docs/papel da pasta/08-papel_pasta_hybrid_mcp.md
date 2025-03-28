# Documentação da Pasta `hybrid_mcp`

## Visão Geral

A pasta `hybrid_mcp` contém uma implementação alternativa do protocolo MCP (Model Context Protocol) utilizando uma arquitetura híbrida que combina Python e Rust. Esta abordagem foi desenvolvida para substituir a implementação original baseada em Node.js e WebAssembly, que apresentava problemas de complexidade, conectividade e compatibilidade.

## Propósito

O propósito principal desta pasta é fornecer:

1. **Implementação Simplificada do MCP**: Uma versão mais direta e manutenível do servidor MCP.
2. **Arquitetura Híbrida**: Combinação estratégica de Python (facilidade de desenvolvimento) e Rust (desempenho).
3. **Compatibilidade com Arcee CLI**: Garantir que o cliente Arcee CLI existente continue funcionando sem modificações.
4. **Servidor Alternativo**: Uma alternativa ao servidor TESS-MCP original que enfrentava diversos problemas.

## Estrutura e Componentes

### Componentes Principais

1. **`fastapi_server.py`**: Implementação de um servidor FastAPI que replica a API do servidor TESS-MCP original, oferecendo:
   - Endpoints compatíveis com o cliente Arcee CLI
   - Sistema de ferramentas MCP (health_check, search_info, process_image, chat_completion)
   - Gestão de agentes e seus arquivos

2. **`app.py`**: Implementação usando o pacote FastMCP, fornecendo:
   - Integração com backend Rust
   - Recursos MCP (chat_history, user_profile)
   - Ferramentas com fallback (buscar_informacao, processar_imagem, chat_completion)
   - Prompts pré-definidos (simple_chat, image_analysis)

3. **`rust_backend.py`**: Interface para comunicação com componentes implementados em Rust, permitindo:
   - Balanceamento de carga entre Python e Rust
   - Delegação de tarefas intensivas para Rust (processamento de imagem)
   - Fallback para Python quando necessário

4. **`simple_mcp.py` e `minimal_mcp.py`**: Implementações simplificadas do cliente MCP para testes e desenvolvimento.

5. **Scripts e Configurações**:
   - `Dockerfile.python`: Containerização da parte Python
   - `docker-compose.yml`: Orquestração da solução completa
   - `start_server.sh`: Script para inicialização do servidor

### Documentação

- **`GUIA-IMPLEMENTACAO-MCP.md`**: Guia detalhado explicando o processo de implementação do servidor TESS-MCP com FastAPI, incluindo:
  - Problema original e suas dificuldades
  - Vantagens da solução adotada
  - Passo a passo da implementação
  - Testes realizados

- **`implementacao_agentes_tess.md`**: Documentação específica sobre a integração com agentes TESS.

## Vantagens da Implementação

1. **Simplicidade**: Implementação mais limpa e direta usando principalmente Python.
2. **Facilidade de Manutenção**: Código mais fácil de entender, modificar e estender.
3. **Compatibilidade**: Mantém as mesmas rotas e formatos de resposta do servidor original.
4. **Desempenho**: Utilização estratégica de Rust para componentes que exigem alto desempenho.
5. **Resiliência**: Sistema de fallback entre Python e Rust para maior robustez.

## Funcionalidades Implementadas

### API MCP

A implementação fornece uma API completa compatível com o protocolo MCP, incluindo:

1. **Verificação de saúde**: Endpoint `/health` para monitoramento.
2. **Listagem de ferramentas**: Endpoint `/api/mcp/tools` para descoberta de capacidades.
3. **Execução de ferramentas**: Endpoint `/api/mcp/execute` para invocar funcionalidades.
4. **Gestão de agentes**: Endpoints para listar, obter detalhes e executar agentes.
5. **Gestão de arquivos**: Endpoints para listar arquivos associados a agentes.

### Ferramentas MCP

A implementação oferece um conjunto de ferramentas MCP essenciais:

1. **health_check**: Verificação da saúde do servidor.
2. **search_info**: Busca de informações sobre tópicos.
3. **process_image**: Processamento e análise de imagens.
4. **chat_completion**: Geração de respostas para prompts de chat.
5. **list_agents**: Listagem de agentes disponíveis.
6. **get_agent**: Obtenção de detalhes sobre agentes específicos.
7. **execute_agent**: Execução de agentes com mensagens específicas.
8. **list_agent_files**: Listagem de arquivos associados a agentes.

## Integração com o Projeto

Esta implementação se integra ao restante do projeto Arcee CLI:

1. **Compatibilidade com Arcee CLI**: Garante que os comandos existentes continuem funcionando.
2. **Suporte aos Agentes TESS**: Preserva a funcionalidade dos agentes TESS.
3. **Infraestrutura Flexível**: Permite a extensão das capacidades do sistema.

## Estado Atual e Recomendações

A implementação atual representa uma alternativa funcional ao servidor TESS-MCP original, com vantagens significativas em termos de simplicidade, manutenção e desempenho. 

Para desenvolvimento futuro, recomenda-se:

1. Expandir a suite de testes automatizados
2. Documentar mais detalhadamente a API REST
3. Aprimorar o balanceamento de carga entre Python e Rust
4. Implementar monitoramento e telemetria mais robustos

## Conclusão

A pasta `hybrid_mcp` fornece uma implementação alternativa do protocolo MCP que resolve problemas significativos da implementação original, mantendo a compatibilidade com o cliente Arcee CLI existente. A arquitetura híbrida Python/Rust oferece um bom equilíbrio entre facilidade de desenvolvimento e desempenho, resultando em um sistema mais robusto e manutenível. 