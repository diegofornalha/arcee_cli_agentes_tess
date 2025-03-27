# Integração da TESS AI com Model Context Protocol (MCP)

Este documento detalha como implementar a integração entre a API da TESS AI e o Model Context Protocol (MCP), permitindo que modelos de IA acessem as funcionalidades da TESS de forma padronizada.

## Visão Geral da Solução

A abordagem implementa:
1. Um servidor MCP que atua como ponte para a API da TESS
2. Capacidades MCP que mapeiam para os endpoints da API da TESS
3. Autenticação e formato de respostas padronizadas

## Detalhes da API TESS

### Base URL e Autenticação

- **Base URL**: `https://api.tess.pareto.io/api`
- **Autenticação**: Token Bearer
- **Header**: `Authorization: Bearer YOUR_API_KEY`
- **Formato**: JSON (`Content-Type: application/json`)
- **Limite de Taxa**: 1 requisição por segundo (entre em contato com o suporte para aumentar)

### Obtenção do API Key

O API key pode ser obtido através de:
1. Dashboard: TESS AI → User Tokens
2. UI: Acessar TESS AI → Menu de Usuário → API Tokens → Add New Token

### Principais Endpoints

| Categoria | Endpoint | Método | Descrição |
|-----------|----------|--------|-----------|
| Agentes | /agents | GET | Listar todos os agentes |
| Agentes | /agents/{id} | GET | Obter um agente específico |
| Agentes | /agents/{id}/execute | POST | Executar um agente |
| Respostas | /agent-responses/{id} | GET | Obter resposta de execução |
| Arquivos de Agente | /agents/{agentId}/files | GET | Listar arquivos de agente |
| Arquivos de Agente | /agents/{agentId}/files | POST | Vincular arquivos ao agente |
| Arquivos de Agente | /agents/{agentId}/files/{fileId} | DELETE | Excluir arquivo de agente |
| Webhooks de Agente | /agents/{id}/webhooks | GET | Listar webhooks de agente |
| Webhooks de Agente | /agents/{id}/webhooks | POST | Criar webhook de agente |
| Arquivos | /files | GET | Listar todos os arquivos |
| Arquivos | /files | POST | Carregar um arquivo |
| Arquivos | /files/{fileId} | GET | Obter detalhes de arquivo |
| Arquivos | /files/{fileId} | DELETE | Excluir um arquivo |
| Arquivos | /files/{fileId}/process | POST | Processar um arquivo |
| Webhooks | /webhooks | GET | Listar todos os webhooks |
| Webhooks | /webhooks/{id} | DELETE | Excluir um webhook |

### Paginação

Controle de paginação com parâmetros:
- **page**: Número da página (padrão: 1, mínimo: 1)
- **per_page**: Itens por página (padrão: 15, mínimo: 1, máximo: 100)

## Implementação do Servidor MCP-TESS

### Configuração do Servidor MCP

```typescript
// TypeScript (mcp-server-tess/src/index.ts)
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import axios from "axios";
import { z } from "zod";

// Inicializa o servidor MCP
const server = new McpServer({
  name: "TessAIConnector",
  version: "1.0.0",
});

// Configuração base para requisições à API da TESS
const TESS_API_BASE_URL = "https://tess.pareto.io/api";
const TESS_API_KEY = process.env.TESS_API_KEY;

// Configura o cliente HTTP com autenticação
const apiClient = axios.create({
  baseURL: TESS_API_BASE_URL,
  headers: {
    "Authorization": `Bearer ${TESS_API_KEY}`,
    "Content-Type": "application/json"
  }
});
```

### Implementação das Capacidades MCP para Agentes

#### Listar Agentes

```typescript
server.tool(
  "listar_agentes_tess",
  {
    page: z.number().optional().describe("Número da página (padrão: 1)"),
    per_page: z.number().optional().describe("Itens por página (padrão: 15, máx: 100)")
  },
  async ({ page = 1, per_page = 15 }: { page?: number; per_page?: number }) => {
    try {
      const response = await apiClient.get("/agents", {
        params: { page, per_page }
      });
      
      return {
        content: [{ 
          type: "text", 
          text: JSON.stringify(response.data) 
        }],
      };
    } catch (error) {
      console.error("Erro ao listar agentes:", error);
      return {
        content: [{ 
          type: "text", 
          text: JSON.stringify({ error: "Falha ao listar agentes" }) 
        }],
      };
    }
  }
);
```

#### Executar um Agente

```typescript
server.tool(
  "executar_agente_tess",
  {
    agent_id: z.string().describe("ID do agente a ser executado"),
    temperature: z.string().optional().describe("Temperatura para geração (0-1)"),
    model: z.string().optional().describe("Modelo a ser usado"),
    messages: z.array(z.object({
      role: z.string(),
      content: z.string()
    })).describe("Mensagens para o agente (formato chat)"),
    tools: z.string().optional().describe("Ferramentas a serem habilitadas"),
    file_ids: z.array(z.number()).optional().describe("IDs dos arquivos a serem anexados"),
    waitExecution: z.boolean().optional().describe("Esperar pela execução completa")
  },
  async ({ 
    agent_id, 
    temperature = "0.5", 
    model = "tess-ai-light", 
    messages, 
    tools = "no-tools", 
    file_ids = [], 
    waitExecution = false 
  }) => {
    try {
      const payload = {
        temperature,
        model,
        messages,
        tools,
        waitExecution,
        file_ids
      };
      
      const response = await apiClient.post(`/agents/${agent_id}/execute`, payload);
      
      return {
        content: [{ 
          type: "text", 
          text: JSON.stringify(response.data) 
        }],
      };
    } catch (error) {
      console.error(`Erro ao executar agente ${agent_id}:`, error);
      return {
        content: [{ 
          type: "text", 
          text: JSON.stringify({ error: `Falha ao executar agente ${agent_id}` }) 
        }],
      };
    }
  }
);
```

### Implementação para Gerenciamento de Arquivos

```typescript
server.tool(
  "upload_arquivo_tess",
  {
    file_path: z.string().describe("Caminho do arquivo a ser enviado"),
    process: z.boolean().optional().describe("Processar o arquivo após o upload")
  },
  async ({ file_path, process = false }: { file_path: string; process?: boolean }) => {
    try {
      const fs = require("fs");
      const FormData = require("form-data");
      const form = new FormData();
      
      // Adiciona o arquivo ao formulário
      form.append("file", fs.createReadStream(file_path));
      
      // Adiciona a opção de processamento
      form.append("process", String(process));
      
      // Configura cabeçalhos específicos para multipart/form-data
      const headers = {
        ...form.getHeaders(),
        "Authorization": `Bearer ${TESS_API_KEY}`
      };
      
      // Faz o upload do arquivo
      const response = await axios.post(`${TESS_API_BASE_URL}/files`, form, { headers });
      
      return {
        content: [{ 
          type: "text", 
          text: JSON.stringify(response.data) 
        }],
      };
    } catch (error) {
      console.error("Erro ao fazer upload de arquivo:", error);
      return {
        content: [{ 
          type: "text", 
          text: JSON.stringify({ error: "Falha ao fazer upload de arquivo" }) 
        }],
      };
    }
  }
);
```

## Inicialização do Servidor MCP

```typescript
// Configuração dos transportes
const stdinTransport = new StdioServerTransport();
server.addTransport(stdinTransport);

// Iniciar o servidor MCP
server.start().catch((err) => {
  console.error("Erro ao iniciar o servidor MCP:", err);
  process.exit(1);
});
```

## Fluxo de uso do MCP-TESS em uma Aplicação

### Exemplo de Fluxo de Uso com Cliente MCP

1. **Inicializar Cliente MCP**:
   ```typescript
   import { McpClient } from "@modelcontextprotocol/sdk/client";
   
   const client = new McpClient({
     transport: "stdio",  // ou "sse" para conexão web
     serverCommand: "node path/to/mcp-server-tess"  // comando para iniciar o servidor
   });
   
   await client.connect();
   ```

2. **Listar Agentes Disponíveis**:
   ```typescript
   const response = await client.runTool("listar_agentes_tess", { per_page: 10 });
   console.log("Agentes disponíveis:", JSON.parse(response.content[0].text));
   ```

3. **Executar um Agente**:
   ```typescript
   const agentId = "123"; // ID obtido da listagem
   
   const response = await client.runTool("executar_agente_tess", {
     agent_id: agentId,
     temperature: "0.7",
     model: "tess-ai-light",
     messages: [
       { role: "user", content: "Olá, pode me ajudar com análise de dados?" }
     ],
     tools: "no-tools"
   });
   
   console.log("Resposta do agente:", JSON.parse(response.content[0].text));
   ```

## Benefícios da Integração MCP-TESS

1. **Acesso Padronizado**: Interface consistente para acessar recursos da TESS via MCP
2. **Segurança Aprimorada**: Tokens de API gerenciados no servidor, não expostos aos clientes
3. **Composabilidade**: Capacidades da TESS podem ser combinadas com outras ferramentas MCP
4. **Controle de Fluxo**: Gerenciamento de limites de taxa e tratamento de erros centralizado
5. **Autonomia para IA**: Modelos de IA podem acessar agentes e funcionalidades da TESS diretamente
6. **Extensibilidade**: Fácil adição de novos endpoints à medida que a API da TESS evolui

## Próximos Passos Possíveis

1. Adicionar suporte para streaming de respostas de agentes
2. Implementar cache local para melhorar o desempenho e reduzir chamadas de API
3. Desenvolver capacidades específicas para casos de uso comum (análise de documentos, geração de conteúdo)
4. Criar interfaces de usuário personalizadas que utilizam o servidor MCP-TESS
5. Implementar tratamento avançado de erros e retentativas para melhorar a robustez
6. Desenvolver componentes de processamento de linguagem natural (NLP) para melhorar a interação em linguagem natural com os agentes da TESS 