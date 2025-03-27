# Servidor TESS com Suporte a MCP

Este é um servidor proxy que integra o TESS (Text Evaluation and Semantic Services) com o MCP (Multi-Channel Platform).

## Requisitos

- Node.js 18+
- Rust e Cargo
- wasm32-wasi target (`rustup target add wasm32-wasi`)

## Configuração

1. Clone o repositório
2. Instale as dependências:
   ```bash
   npm install
   ```
3. Configure as variáveis de ambiente no arquivo `.env`:
   ```
   PORT=3000
   MCP_API_KEY=seu_mcp_api_key
   MCP_API_URL=https://www.mcp.run/api
   MCP_SSE_URL=https://www.mcp.run/api/sse
   ```

## Build

Para compilar o plugin WebAssembly:

```bash
npm run build
```

## Execução

Para iniciar o servidor:

```bash
npm start
```

Para desenvolvimento com hot-reload:

```bash
npm run dev
```

## Endpoints

### Health Check
- GET `/health`
- Verifica se o servidor está funcionando

### Listar Ferramentas MCP
- GET `/api/mcp/tools`
- Query params:
  - `session_id`: ID da sessão MCP
  - `mcp_sse_url`: URL do SSE do MCP

### Executar Ferramenta MCP
- POST `/api/mcp/execute`
- Query params:
  - `session_id`: ID da sessão MCP
  - `mcp_sse_url`: URL do SSE do MCP
- Body:
  ```json
  {
    "tool": "nome_da_ferramenta",
    "params": {
      // parâmetros específicos da ferramenta
    }
  }
  ```

## Arquitetura

O servidor é composto por:

1. **Node.js + Express**: Servidor HTTP que recebe as requisições
2. **Plugin Rust/WebAssembly**: Lógica principal que processa as requisições
3. **Proxy MCP**: Encaminha requisições para o MCP.run

## Desenvolvimento

O código do plugin está em Rust e é compilado para WebAssembly. O servidor Node.js carrega este plugin e o utiliza para processar as requisições.

Para modificar o comportamento do servidor:

1. Edite o código Rust em `src/lib.rs`
2. Recompile o plugin com `npm run build`
3. Reinicie o servidor

## Logs e Monitoramento

O servidor registra logs para:
- Inicialização do servidor
- Erros de processamento
- Chamadas de API

## Segurança

- Todas as requisições devem incluir um `session_id` válido
- As credenciais do MCP são configuradas via variáveis de ambiente
- CORS está habilitado para desenvolvimento

## Troubleshooting

Se encontrar problemas:

1. Verifique se o plugin foi compilado corretamente
2. Confirme que as variáveis de ambiente estão configuradas
3. Verifique os logs do servidor
4. Certifique-se que o MCP.run está acessível 