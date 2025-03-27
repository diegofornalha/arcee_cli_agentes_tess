import {
      BlobResourceContents,
      CallToolRequest,
      CallToolResult,
      Content,
      ContentType,
      ListToolsResult,
      Params,
      Role,
      TextAnnotation,
      TextResourceContents,
      ToolDescription,
  } from './pdk'

/**
 * Lista de ferramentas disponíveis na API TESS
 */
const TESS_TOOLS: ToolDescription[] = [
  {
    name: "listar_agentes_tess",
    description: "Lista todos os agentes disponíveis na API TESS",
    inputSchema: {
      type: "object",
      properties: {
        page: { type: "number", description: "Número da página (padrão: 1)" },
        per_page: { type: "number", description: "Itens por página (padrão: 15, máx: 100)" }
      }
    }
  },
  {
    name: "obter_agente_tess",
    description: "Obtém detalhes de um agente específico",
    inputSchema: {
      type: "object",
      required: ["agent_id"],
      properties: {
        agent_id: { type: "string", description: "ID do agente a ser consultado" }
      }
    }
  },
  {
    name: "executar_agente_tess",
    description: "Executa um agente com mensagens específicas",
    inputSchema: {
      type: "object",
      required: ["agent_id", "messages"],
      properties: {
        agent_id: { type: "string", description: "ID do agente a ser executado" },
        temperature: { type: "string", description: "Temperatura para geração (0-1)" },
        model: { type: "string", description: "Modelo a ser usado" },
        messages: { type: "string", description: "Mensagens para o agente (formato chat JSON)" },
        tools: { type: "string", description: "Ferramentas a serem habilitadas" },
        file_ids: { type: "string", description: "IDs dos arquivos a serem anexados (JSON array)" },
        waitExecution: { type: "boolean", description: "Esperar pela execução completa" }
      }
    }
  },
  {
    name: "listar_arquivos_agente_tess",
    description: "Lista todos os arquivos associados a um agente",
    inputSchema: {
      type: "object",
      required: ["agent_id"],
      properties: {
        agent_id: { type: "string", description: "ID do agente" },
        page: { type: "number", description: "Número da página (padrão: 1)" },
        per_page: { type: "number", description: "Itens por página (padrão: 15, máx: 100)" }
      }
    }
  }
];

/**
 * Called when the tool is invoked. 
 * If you support multiple tools, you must switch on the input.params.name to detect which tool is being called.
 *
 * @param {CallToolRequest} input - The incoming tool request from the LLM
 * @returns {CallToolResult} The servlet's response to the given tool call
 */
export function callImpl(input: CallToolRequest): CallToolResult {
  const toolName = input.params.name;
  
  // Verifica se a ferramenta existe
  const toolExists = TESS_TOOLS.some(tool => tool.name === toolName);
  if (!toolExists) {
    return {
      content: [
        {
          type: ContentType.Text,
          text: JSON.stringify({ error: `Ferramenta "${toolName}" não encontrada` })
        }
      ]
    };
  }
  
  // TODO: Implementar a chamada real para a API TESS
  // Por enquanto, retorna uma resposta simulada
  return {
    content: [
      {
        type: ContentType.Text,
        text: JSON.stringify({ 
          message: `Simulação da chamada à ferramenta ${toolName}`,
          params: input.params,
          status: "success" 
        })
      }
    ]
  };
}

/**
 * Called by mcpx to understand how and why to use this tool.
 * Note: Your servlet configs will not be set when this function is called,
 * so do not rely on config in this function
 *
 * @returns {ListToolsResult} The tools' descriptions, supporting multiple tools from a single servlet.
 */
export function describeImpl(): ListToolsResult {
  return {
    tools: TESS_TOOLS
  };
}



