# Arquitetura Híbrida MCP (Python + Rust)

Este projeto implementa uma arquitetura híbrida para MCP (Model Context Protocol) que combina:

1. **Frontend Python** usando o SDK oficial MCP
2. **Backend Rust** usando a implementação customizada TESS-MCP

Esta abordagem híbrida fornece o melhor dos dois mundos: a facilidade de desenvolvimento do Python com o desempenho e segurança do Rust.

## Estrutura do Projeto

```
hybrid_mcp/
├── app.py                 # Servidor MCP Python
├── rust_backend.py        # Cliente Python para o backend Rust
├── requirements.txt       # Dependências Python
├── Dockerfile.python      # Dockerfile para o serviço Python
├── docker-compose.yml     # Configuração para ambos os serviços
└── README.md              # Este arquivo

mcp-server-agno-xtp/
├── src/                   # Código-fonte Rust
├── server.js              # Servidor Node.js para o plugin WASM
├── Dockerfile             # Dockerfile para o serviço Rust
└── ... (outros arquivos)
```

## Características

- **Execução paralela**: Ambos os serviços operam simultaneamente
- **Fallback automático**: Se um backend falhar, o outro assume
- **Balanceamento de carga**: Tarefas de CPU intensivas vão para o Rust
- **Estratégia de Desenvolvimento Gradual**: Comece com Python, migre para Rust conforme necessário

## Recursos MCP disponíveis

### Recursos (Resources)

- `chat_history://{chat_id}` - Histórico de conversas
- `user_profile://{user_id}` - Perfis de usuário

### Ferramentas (Tools)

- `buscar_informacao` - Pesquisa informações com fallback
- `processar_imagem` - Processamento de imagens (principalmente no Rust)
- `chat_completion` - Balanceamento de carga para prompts grandes/pequenos

### Prompts

- `simple_chat` - Prompt simples para chat
- `image_analysis` - Prompt para análise de imagens

## Requisitos

- Docker e Docker Compose
- Python 3.9+
- Rust 1.65+
- Node.js 18+

## Executando o projeto

### Usando Docker Compose (Recomendado)

```bash
# Na raiz do projeto
docker-compose up -d
```

### Desenvolvimento local

1. Inicie o backend Rust:

```bash
cd mcp-server-agno-xtp
cargo build --target wasm32-wasip1 --release
npm install
npm run dev
```

2. Em outro terminal, inicie o frontend Python:

```bash
cd hybrid_mcp
pip install -r requirements.txt
python app.py
```

## Testando com Claude Desktop

1. Instale o servidor MCP Python no Claude Desktop:

```bash
cd hybrid_mcp
mcp install app.py
```

2. Interact com o Claude usando as ferramentas e prompts disponíveis

## Exemplos de uso

### Obter histórico de chat

```python
from mcp import ClientSession
import asyncio

async def main():
    async with ClientSession("http://localhost:8000") as session:
        content, _ = await session.read_resource("chat_history://123")
        print(content)

asyncio.run(main())
```

### Executar processamento de imagem

```python
from mcp import ClientSession
import asyncio

async def main():
    async with ClientSession("http://localhost:8000") as session:
        result = await session.call_tool("processar_imagem", {
            "image_url": "https://example.com/image.jpg"
        })
        print(result)

asyncio.run(main())
```

## Desenvolvimento e Contribuição

### Adicionando novos recursos ao Python

Edite `app.py` e adicione novos decoradores `@mcp.resource()` ou `@mcp.tool()`.

### Adicionando novas funcionalidades ao Rust

Edite `mcp-server-agno-xtp/src/lib.rs` e atualize a lógica de correspondência de rota para `("/api/mcp/execute")` no handler.

## Configuração Avançada

Você pode configurar esta aplicação através de variáveis de ambiente:

- `PORT` - Porta para o servidor Python (padrão: 8000)
- `RUST_BACKEND_URL` - URL para o backend Rust (padrão: http://localhost:3000)
- `MCP_API_KEY` - Chave de API para MCP.run (opcional) 