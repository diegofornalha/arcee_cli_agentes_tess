use extism_pdk::*;
use serde::{Deserialize, Serialize};
use reqwest::Client;
use std::collections::HashMap;
use anyhow::{Result, anyhow};

#[derive(Deserialize)]
struct Request {
    method: String,
    path: String,
    body: String,
    query: Option<HashMap<String, String>>,
    headers: Option<HashMap<String, String>>
}

#[derive(Serialize)]
struct Response {
    status: u16,
    body: String,
    headers: HashMap<String, String>
}

#[derive(Serialize, Deserialize)]
struct MCPToolsResponse {
    tools: Vec<MCPTool>
}

#[derive(Serialize, Deserialize)]
struct MCPTool {
    name: String,
    description: String,
    parameters: Option<serde_json::Value>
}

#[derive(Serialize, Deserialize)]
struct MCPExecuteRequest {
    tool: String,
    params: Option<serde_json::Value>
}

#[derive(Serialize, Deserialize)]
struct ImageProcessingResult {
    width: u32,
    height: u32,
    format: String,
    has_faces: bool,
    description: String,
    tags: Vec<String>,
}

#[derive(Serialize, Deserialize)]
struct ChatCompletionRequest {
    prompt: String,
    history: Option<Vec<String>>,
}

#[plugin_fn]
pub fn handle_request(request: Json<Request>) -> FnResult<Json<Response>> {
    let req = request.into_inner();
    
    // Configurar headers padrão
    let mut headers = HashMap::new();
    headers.insert("Content-Type".to_string(), "application/json".to_string());
    
    match (req.method.as_str(), req.path.as_str()) {
        // Health check
        ("GET", "/health") => {
            Ok(Json(Response {
                status: 200,
                body: r#"{"status":"ok","message":"TESS proxy server is running"}"#.to_string(),
                headers
            }))
        },
        
        // Listar ferramentas MCP
        ("GET", "/api/mcp/tools") => {
            let session_id = req.query.as_ref()
                .and_then(|q| q.get("session_id"))
                .ok_or_else(|| anyhow!("session_id não fornecido"))?;
                
            // Se houver um parâmetro resource, processa como solicitação de recurso
            if let Some(resource) = req.query.as_ref().and_then(|q| q.get("resource")) {
                if resource.starts_with("chat_history://") {
                    let chat_id = resource.strip_prefix("chat_history://").unwrap_or("unknown");
                    return Ok(Json(Response {
                        status: 200,
                        body: format!("Histórico de chat {} (via Rust): Recuperado em {}", 
                                      chat_id, chrono::Utc::now().to_rfc3339()),
                        headers
                    }));
                }
                
                // Recurso não suportado
                return Ok(Json(Response {
                    status: 404,
                    body: format!("{{\"error\":\"Recurso não encontrado\",\"resource\":\"{}\"}}", resource),
                    headers
                }));
            }
                
            // Fazer requisição para o MCP.run
            let client = Client::new();
            let rt = tokio::runtime::Builder::new_current_thread()
                .enable_all()
                .build()?;
                
            let response = rt.block_on(async {
                client.get("https://www.mcp.run/api/mcp/get-tools")
                    .query(&[("session_id", session_id)])
                    .send()
                    .await
            })?;
            
            let status = response.status();
            
            if !status.is_success() {
                let error_text = rt.block_on(async {
                    response.text().await
                })?;
                
                return Ok(Json(Response {
                    status: status.as_u16(),
                    body: error_text,
                    headers
                }));
            }
            
            // Processar e retornar ferramentas
            let tools: Vec<MCPTool> = rt.block_on(async {
                response.json().await
            })?;
            
            let response_body = serde_json::to_string(&MCPToolsResponse { tools })?;
            
            Ok(Json(Response {
                status: 200,
                body: response_body,
                headers
            }))
        },
        
        // Executar ferramenta MCP
        ("POST", "/api/mcp/execute") => {
            let session_id = req.query.as_ref()
                .and_then(|q| q.get("session_id"))
                .ok_or_else(|| anyhow!("session_id não fornecido"))?;
                
            // Parsear corpo da requisição
            let execute_req: MCPExecuteRequest = serde_json::from_str(&req.body)?;
            
            // Processar ferramentas locais
            match execute_req.tool.as_str() {
                "health_check" => {
                    // Health check simples
                    return Ok(Json(Response {
                        status: 200,
                        body: r#"{"status":"ok","message":"Rust backend is healthy"}"#.to_string(),
                        headers
                    }));
                },
                "search_info" => {
                    // Implementação de pesquisa em Rust
                    if let Some(params) = &execute_req.params {
                        if let Some(query) = params.get("query").and_then(|q| q.as_str()) {
                            let result = format!(
                                "Resultados para '{}' (via Rust): Encontrados 3 documentos relevantes em {}.", 
                                query, chrono::Utc::now().to_rfc3339()
                            );
                            return Ok(Json(Response {
                                status: 200,
                                body: result,
                                headers
                            }));
                        }
                    }
                    return Ok(Json(Response {
                        status: 400,
                        body: r#"{"error":"Parâmetro 'query' não fornecido"}"#.to_string(),
                        headers
                    }));
                },
                "process_image" => {
                    // Processamento de imagem (simulado)
                    if let Some(params) = &execute_req.params {
                        if let Some(url) = params.get("url").and_then(|u| u.as_str()) {
                            // Simulação de processamento de imagem
                            let result = ImageProcessingResult {
                                width: 800,
                                height: 600,
                                format: "jpeg".to_string(),
                                has_faces: true,
                                description: format!("Imagem em {} processada via backend Rust", url),
                                tags: vec!["imagem".to_string(), "processada".to_string(), "rust".to_string()],
                            };
                            
                            return Ok(Json(Response {
                                status: 200,
                                body: serde_json::to_string(&result)?,
                                headers
                            }));
                        }
                    }
                    return Ok(Json(Response {
                        status: 400,
                        body: r#"{"error":"Parâmetro 'url' não fornecido"}"#.to_string(),
                        headers
                    }));
                },
                "chat_completion" => {
                    // Processamento de chat completion
                    if let Some(params) = &execute_req.params {
                        let chat_req: ChatCompletionRequest = serde_json::from_value(params.clone())?;
                        
                        // Simulação de resposta do chat
                        let response = format!(
                            "Resposta Rust para: {}... (processada em {})",
                            &chat_req.prompt[..std::cmp::min(50, chat_req.prompt.len())],
                            chrono::Utc::now().to_rfc3339()
                        );
                        
                        return Ok(Json(Response {
                            status: 200,
                            body: response,
                            headers
                        }));
                    }
                    return Ok(Json(Response {
                        status: 400,
                        body: r#"{"error":"Parâmetros inválidos para chat completion"}"#.to_string(),
                        headers
                    }));
                },
                _ => {
                    // Se a ferramenta não for local, encaminha para o MCP.run
                    // Preparar dados para o MCP.run
                    let mut mcp_data = HashMap::new();
                    mcp_data.insert("session_id", session_id.to_string());
                    mcp_data.insert("tool", execute_req.tool);
                    
                    if let Some(params) = execute_req.params {
                        mcp_data.insert("params", params.to_string());
                    }
                    
                    // Fazer requisição para o MCP.run
                    let client = Client::new();
                    let rt = tokio::runtime::Builder::new_current_thread()
                        .enable_all()
                        .build()?;
                        
                    let response = rt.block_on(async {
                        client.post("https://www.mcp.run/api/mcp/tool-call")
                            .json(&mcp_data)
                            .send()
                            .await
                    })?;
                    
                    let status = response.status();
                    let response_text = rt.block_on(async {
                        response.text().await
                    })?;
                    
                    Ok(Json(Response {
                        status: status.as_u16(),
                        body: response_text,
                        headers
                    }))
                }
            }
        },
        
        // Rota não encontrada
        _ => Ok(Json(Response {
            status: 404,
            body: r#"{"error":"Endpoint não encontrado"}"#.to_string(),
            headers
        }))
    }
} 