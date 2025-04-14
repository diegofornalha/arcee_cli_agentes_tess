# Documentação da Pasta `mcp-server-agno-xtp`

## Visão Geral

A pasta `mcp-server-agno-xtp` contém um servidor proxy que integra o TESS (Text Evaluation and Semantic Services) com o protocolo MCP (Model Context Protocol). Este componente atua como uma ponte entre aplicações cliente e os serviços TESS, implementando uma API compatível com o protocolo MCP usando uma arquitetura híbrida que combina Node.js, Rust e WebAssembly.

## Propósito

O propósito principal desta pasta é:

1. **Integração MCP-TESS**: Fornecer um servidor proxy que permite que aplicações compatíveis com MCP (como o Arcee CLI) se comuniquem com os serviços TESS.
2. **Processamento Eficiente**: Utilizar o Rust compilado para WebAssembly para operações de processamento intensivo.
3. **API Unificada**: Expor uma API HTTP padronizada para recursos e ferramentas MCP.
4. **Servidor Independente**: Oferecer um serviço que pode ser executado localmente ou em contêineres.

## Arquitetura

A arquitetura do servidor é baseada em três componentes principais:

1. **Servidor Node.js/Express**: Responsável por receber requisições HTTP e gerenciar o ciclo de vida das solicitações.
2. **Plugin Rust/WebAssembly**: Contém a lógica principal de processamento, compilada para WebAssembly e carregada pelo servidor Node.js.
3. **Integração FastAPI** (pasta hybrid_mcp): Implementação alternativa em Python que oferece os mesmos endpoints, servindo como solução de fallback.

```
mcp-server-agno-xtp/
│
├── server.js                 # Servidor Express que gerencia requisições HTTP
├── src/                      # Código Rust compilado para WebAssembly
│   └── lib.rs                # Implementação das ferramentas MCP em Rust
├── hybrid_mcp/               # Implementação alternativa em Python/FastAPI
│   └── fastapi_server.py     # Servidor FastAPI que implementa os mesmos endpoints
├── setup.sh                  # Script para configuração do ambiente
└── package.json              # Configuração NPM e scripts
```

## Componentes Principais

### 1. Servidor Node.js (server.js)

O servidor Express gerencia o ciclo de vida das requisições HTTP e atua como ponte para o código WebAssembly:

- Inicializa o plugin WebAssembly
- Expõe endpoints para health check e operações MCP
- Gerencia erros e formatação de respostas
- Implementa middleware CORS e parsing JSON

### 2. Plugin Rust (src/lib.rs)

O código Rust implementa a lógica principal de processamento:

- Define estruturas para requisições e respostas
- Implementa o handler principal (`handle_request`)
- Fornece implementações específicas para ferramentas MCP:
  - `health_check`: Verificação de saúde do servidor
  - `search_info`: Busca de informações
  - `process_image`: Processamento de imagens
  - `chat_completion`: Complementação de chat

### 3. Implementação FastAPI (hybrid_mcp/fastapi_server.py)

Uma implementação Python que oferece os mesmos endpoints:

- Servidor FastAPI completo
- Implementações nativas das ferramentas MCP
- Estrutura de rotas compatível com a versão Node.js/Rust

## Endpoints da API

O servidor expõe os seguintes endpoints:

1. **Health Check**
   - `GET /health`: Verifica se o servidor está funcionando corretamente.

2. **Listar Ferramentas MCP**
   - `GET /api/mcp/tools?session_id={id}`: Lista as ferramentas MCP disponíveis.

3. **Executar Ferramenta MCP**
   - `POST /api/mcp/execute?session_id={id}`: Executa uma ferramenta MCP específica.

## Ferramentas MCP Implementadas

1. **health_check**: Verifica a saúde do servidor.
2. **search_info**: Busca informações sobre um tópico.
3. **process_image**: Processa uma imagem e retorna informações.
4. **chat_completion**: Gera resposta para um prompt de chat.

## Integração com Arcee CLI

Esta pasta fornece o servidor MCP necessário para que o Arcee CLI possa se comunicar com os serviços TESS. O Arcee CLI se conecta a este servidor para:

1. Descobrir ferramentas disponíveis
2. Executar agentes TESS via protocolo MCP
3. Acessar recursos TESS em um formato padronizado

## Desafios e Soluções

Durante o desenvolvimento, vários desafios foram enfrentados e solucionados:

1. **Configuração Rust/WebAssembly**: Configuração correta do ambiente Rust com target `wasm32-wasip1`.
2. **Limitações Tokio**: Adaptação das features do Tokio para compatibilidade com WebAssembly.
3. **Integração Extism**: Configuração adequada do manifesto e carregamento do plugin WebAssembly.
4. **Gerenciamento de Memória**: Cuidados com lifetimes e ownership em Rust para WebAssembly.

## Estado Atual e Alternativas

Atualmente, o projeto possui duas implementações paralelas:

1. **Implementação Original (Node.js + Rust/WebAssembly)**: Abordagem original que combina as vantagens do JavaScript para API web e Rust para processamento eficiente.

2. **Implementação Alternativa (Python/FastAPI)**: Solução mais simples e direta que implementa os mesmos endpoints usando apenas Python, desenvolvida para contornar problemas da implementação original.

A implementação FastAPI (`hybrid_mcp/fastapi_server.py`) foi criada como uma alternativa mais simples e confiável, mas o projeto mantém ambas as abordagens, permitindo escolher a mais adequada para cada contexto.

## Recomendações

Para desenvolvimento futuro, sugere-se:

1. **Unificação de Implementações**: Considerar a adoção completa da implementação FastAPI como padrão, devido à sua simplicidade e manutenibilidade.
2. **Ampliação de Testes**: Implementar testes automatizados para garantir a compatibilidade entre as diferentes implementações.
3. **Documentação da API**: Expandir a documentação dos endpoints e ferramentas disponíveis.
4. **Containerização**: Aprimorar a infraestrutura de containerização para facilitar a implantação.

## Conclusão

A pasta `mcp-server-agno-xtp` desempenha um papel fundamental no ecossistema Arcee CLI, fornecendo a ponte necessária entre o protocolo MCP e os serviços TESS. A arquitetura híbrida oferece opções de implementação, permitindo escolher entre desempenho (Node.js + Rust/WebAssembly) ou simplicidade (Python/FastAPI) conforme as necessidades do projeto. 