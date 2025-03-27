# Guia de Implementação: Ferramentas de Agentes TESS no Servidor MCP

Este documento explica passo a passo como implementar funcionalidades relacionadas a agentes no servidor TESS MCP usando o FastAPI.

## Visão Geral

A implementação adicionou quatro funcionalidades principais:

1. `list_agents` - Listar agentes disponíveis com paginação
2. `get_agent` - Obter detalhes de um agente específico
3. `execute_agent` - Executar um agente com mensagens específicas
4. `list_agent_files` - Listar arquivos associados a um agente

## Passo 1: Implementar funções na classe MCPTools

O primeiro passo foi implementar os métodos na classe `MCPTools` que contém a lógica de negócio:

```python
# Exemplo de implementação da função list_agents com paginação
@staticmethod
async def list_agents(page: int = 1, per_page: int = 15) -> Dict[str, Any]:
    """Lista os agentes disponíveis no sistema"""
    logger.info(f"Listando agentes disponíveis (página {page}, {per_page} por página)")
    
    # Obter lista de agentes (neste exemplo é simulada, mas poderia vir de um banco de dados)
    all_agents = [
        # Lista de agentes aqui...
    ]
    
    # Aplicar paginação
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_agents = all_agents[start_idx:end_idx]
    
    # Retornar resultado com metadados de paginação
    return {
        "agents": paginated_agents,
        "total": len(all_agents),
        "page": page,
        "per_page": per_page,
        "total_pages": (len(all_agents) + per_page - 1) // per_page
    }
```

Desta forma, implementei todas as quatro funções seguindo o mesmo padrão:
1. Definir o método estático com os parâmetros adequados
2. Adicionar logging para rastreabilidade
3. Implementar a lógica de negócio (neste caso simulada)
4. Retornar os resultados no formato adequado

## Passo 2: Atualizar a lista de ferramentas disponíveis

Adicionei as novas ferramentas à lista retornada pelo endpoint `/api/mcp/tools`:

```python
@app.get("/api/mcp/tools")
async def list_tools(request: Request):
    """Lista as ferramentas MCP disponíveis"""
    # Verificação do session_id e outros códigos...
    
    tools = [
        # Ferramentas existentes...
        {
            "name": "list_agents",
            "description": "Lista os agentes disponíveis no sistema",
            "parameters": {
                "page": {"type": "number", "description": "Número da página (padrão: 1)"},
                "per_page": {"type": "number", "description": "Itens por página (padrão: 15, máx: 100)"}
            }
        },
        {
            "name": "get_agent",
            "description": "Obtém detalhes de um agente específico",
            "parameters": {
                "agent_id": {"type": "string", "description": "ID do agente a ser consultado"}
            }
        },
        # Outras ferramentas novas...
    ]
    
    return {"tools": tools}
```

Isso permite que os clientes descubram as novas ferramentas disponíveis e seus parâmetros.

## Passo 3: Implementar o tratamento no endpoint de execução

Adicionei o código para tratar as novas ferramentas no endpoint `/api/mcp/execute`:

```python
@app.post("/api/mcp/execute")
async def execute_tool(request: Request):
    """Executa uma ferramenta MCP"""
    # Código existente para obter tool_name e params...
    
    try:
        # Ferramentas existentes...
        
        elif tool_name == "list_agents":
            page = int(params.get("page", 1))
            per_page = min(int(params.get("per_page", 15)), 100)  # Limita a 100 por página
            result = await MCPTools.list_agents(page, per_page)
            return {"body": json.dumps(result)}
        
        elif tool_name == "get_agent":
            agent_id = params.get("agent_id")
            if not agent_id:
                raise HTTPException(status_code=400, detail="Parâmetro 'agent_id' não fornecido")
            
            result = await MCPTools.get_agent(agent_id)
            return {"body": json.dumps(result)}
        
        # Outras ferramentas novas...
```

Para cada ferramenta, as etapas são:
1. Extrair os parâmetros necessários
2. Validar os parâmetros obrigatórios
3. Chamar o método correspondente da classe `MCPTools`
4. Converter o resultado para JSON e retornar

## Passo 4: Verificação e testes

Após implementar as mudanças, realizei testes para verificar o funcionamento:

1. **Verificar listagem de ferramentas**:
   ```bash
   curl http://localhost:3000/api/mcp/tools?session_id=test
   ```

2. **Testar ferramenta de listagem de agentes**:
   ```bash
   curl -X POST http://localhost:3000/api/mcp/execute?session_id=test \
     -H "Content-Type: application/json" \
     -d '{"tool": "list_agents", "params": {"page": 1, "per_page": 2}}'
   ```

3. **Testar ferramenta de obtenção de detalhes de agente**:
   ```bash
   curl -X POST http://localhost:3000/api/mcp/execute?session_id=test \
     -H "Content-Type: application/json" \
     -d '{"tool": "get_agent", "params": {"agent_id": "agent-002"}}'
   ```

4. **Testar via Arcee CLI**:
   ```bash
   arcee mcp listar
   arcee mcp executar list_agents
   arcee mcp executar get_agent --params '{"agent_id": "agent-002"}'
   ```

## Considerações para Novas Implementações

Ao implementar novas funcionalidades, siga estes passos:

1. **Adicione o método na classe MCPTools**:
   - Defina parâmetros, tipo de retorno e docstring
   - Implemente a lógica de negócio
   - Adicione tratamento de erros adequado

2. **Registre a ferramenta na lista de ferramentas**:
   - Adicione um novo item no array `tools` em `list_tools`
   - Defina nome, descrição e especifique os parâmetros com seus tipos e descrições

3. **Implemente o manipulador no endpoint de execução**:
   - Adicione um novo bloco `elif` para sua ferramenta em `execute_tool`
   - Extraia e valide os parâmetros
   - Chame o método apropriado e retorne o resultado

4. **Teste a nova funcionalidade**:
   - Verifique se a ferramenta aparece na listagem
   - Teste a execução com parâmetros válidos e inválidos
   - Teste através da CLI ou outras interfaces

## Exemplo Prático: Adicionar uma Nova Ferramenta

Para adicionar uma nova ferramenta chamada `create_agent`, você seguiria estes passos:

1. **Implementar na classe MCPTools**:
   ```python
   @staticmethod
   async def create_agent(name: str, description: str, capabilities: list = None) -> Dict[str, Any]:
       """Cria um novo agente no sistema"""
       logger.info(f"Criando novo agente: {name}")
       
       # Lógica para criar o agente
       new_agent_id = f"agent-{datetime.now().strftime('%Y%m%d%H%M%S')}"
       
       return {
           "id": new_agent_id,
           "name": name,
           "description": description,
           "capabilities": capabilities or [],
           "created_at": datetime.now().isoformat(),
           "status": "active"
       }
   ```

2. **Adicionar na lista de ferramentas**:
   ```python
   {
       "name": "create_agent",
       "description": "Cria um novo agente no sistema",
       "parameters": {
           "name": {"type": "string", "description": "Nome do agente"},
           "description": {"type": "string", "description": "Descrição do agente"},
           "capabilities": {"type": "array", "description": "Lista de capacidades do agente (opcional)"}
       }
   }
   ```

3. **Implementar o manipulador**:
   ```python
   elif tool_name == "create_agent":
       name = params.get("name")
       description = params.get("description")
       
       if not name or not description:
           raise HTTPException(status_code=400, detail="Parâmetros 'name' e 'description' são obrigatórios")
       
       capabilities = params.get("capabilities", [])
       result = await MCPTools.create_agent(name, description, capabilities)
       return {"body": json.dumps(result)}
   ```

## Conclusão

Seguindo este padrão, você pode facilmente estender o servidor MCP com novas funcionalidades. A arquitetura modular facilita a adição de novos recursos sem afetar o código existente.

A implementação das funcionalidades de agentes TESS demonstra como expandir o servidor MCP para suportar diferentes tipos de recursos e operações CRUD (criar, ler, atualizar, excluir) seguindo boas práticas de desenvolvimento. 