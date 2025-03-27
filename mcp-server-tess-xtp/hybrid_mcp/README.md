# Servidor TESS-MCP com FastAPI

Este é um servidor compatível com a API do TESS-MCP, implementado em Python usando FastAPI. 
O servidor mantém a mesma interface que a versão Node.js + Rust, tornando-o compatível com o cliente Arcee CLI.

## Características

- Implementação completa das rotas do TESS-MCP
- Compatibilidade total com o Arcee CLI
- Roda na porta 3000 por padrão (mesma porta do servidor original)
- Fácil de estender com novas ferramentas

## Ferramentas Implementadas

1. **health_check** - Verifica a saúde do servidor
2. **search_info** - Busca informações sobre um tópico
3. **process_image** - Processa uma imagem e retorna informações
4. **chat_completion** - Gera respostas para prompts de texto

## Requisitos

```
fastapi>=0.100.0
uvicorn>=0.24.0
pydantic>=2.5.0
aiohttp>=3.9.0
python-dotenv>=1.0.0
requests>=2.31.0
asyncio>=3.4.3
```

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

1. Iniciar o servidor:

```bash
python fastapi_server.py
```

2. Testar o servidor:

```bash
# Verificar saúde
curl http://localhost:3000/health

# Listar ferramentas
curl "http://localhost:3000/api/mcp/tools?session_id=test"

# Executar uma ferramenta
curl -X POST "http://localhost:3000/api/mcp/execute?session_id=test" \
     -H "Content-Type: application/json" \
     -d '{"tool":"search_info","params":{"query":"Python"}}'
```

3. Usar com Arcee CLI:

```bash
# O Arcee CLI já está configurado para usar http://localhost:3000/api
arcee mcp listar
arcee mcp executar search_info --query "Python"
```

## Como Estender

Para adicionar novas ferramentas, siga estes passos:

1. Adicione um novo método estático à classe `MCPTools`
2. Adicione a ferramenta à lista no endpoint `/api/mcp/tools`
3. Adicione a lógica de execução no endpoint `/api/mcp/execute`

## Notas

Este servidor é um substituto direto para o servidor TESS-MCP original em Node.js + Rust,
fornecendo uma alternativa em Python mais fácil de modificar e estender. 