# Guia de Publicação: MCP-Server-TESS-XTP no MCP.run

Este guia detalha o processo completo para publicar e atualizar o plugin MCP-Server-TESS-XTP na plataforma MCP.run, desde a configuração inicial até o processo de atualização.

## Pré-requisitos

Antes de começar, você precisa ter:

- Node.js (versão 16 ou superior)
- npm ou yarn
- CLI XTP instalada
- Uma conta no MCP.run
- Token de acesso XTP
- Git instalado (para versionamento)

## 1. Instalação da CLI XTP

A CLI XTP é necessária para compilar e publicar o plugin. Instale-a com:

```bash
curl "https://static.dylibso.com/cli/install.sh" -s | bash
```

Verifique a instalação:

```bash
xtp --version
```

## 2. Autenticação na plataforma XTP

Há duas maneiras de autenticar:

### Método 1: Login interativo

Execute o comando de login:

```bash
xtp login
```

Isso abrirá uma janela do navegador para autenticação.

### Método 2: Token de acesso (recomendado para CI/CD)

Configure o token de acesso como variável de ambiente:

```bash
export XTP_TOKEN=xtp0_SEU_TOKEN_AQUI
```

Exemplo com o token usado anteriormente:

```bash
export XTP_TOKEN=xtp0_AZXRKn90dEmxthgTLM5EwvTuX-rzoZjD7O85UpdlYsN2BFyJRCihkw
```

## 3. Configuração do projeto

### Clonando o repositório (se ainda não tiver feito)

```bash
git clone https://github.com/diegofornalha/mcp-server-tess-xtp.git
cd mcp-server-tess-xtp
```

### Instalando dependências

```bash
npm install
```

## 4. Desenvolvimento do plugin

O plugin está estruturado da seguinte forma:

- `src/main.ts`: Implementação principal das ferramentas TESS
- `src/pdk.ts`: Tipos e definições para o Plugin Development Kit
- `xtp.toml`: Configuração do plugin XTP

Ao modificar o plugin, foque no arquivo `src/main.ts` que contém as implementações das ferramentas TESS. As principais funções são:

- `callImpl()`: Chamada quando uma ferramenta é invocada
- `describeImpl()`: Fornece informações sobre as ferramentas disponíveis

### Adicionando uma nova ferramenta

Para adicionar uma nova ferramenta:

1. Adicione-a à lista `TESS_TOOLS` em `src/main.ts`
2. Implemente a lógica no switch case dentro de `callImpl()`

Exemplo:

```typescript
// Adicionar à lista TESS_TOOLS
{
  name: "nova_ferramenta_tess",
  description: "Descrição da nova ferramenta",
  inputSchema: {
    type: "object",
    properties: {
      parametro1: { type: "string", description: "Descrição do parâmetro" }
    }
  }
}

// Implementar no switch case
case "nova_ferramenta_tess":
  result = await minhaNovaFerramenta(params);
  break;
```

## 5. Compilação e teste

### Preparando o ambiente de compilação

O script `prepare.sh` instala as dependências necessárias para a compilação:

```bash
bash prepare.sh
```

### Compilando o plugin

```bash
npm run build
```

Isso criará um arquivo WebAssembly na pasta `dist/`.

## 6. Publicação no MCP.run

### Primeira publicação

Após compilar o plugin, você pode publicá-lo com:

```bash
xtp plugin push
```

Este comando utiliza as configurações do arquivo `xtp.toml` para publicar o plugin.

### Verificando a publicação

Para verificar se o plugin foi publicado corretamente:

```bash
xtp plugin view --name 'mcp-server-tess' --extension-point ext_01je4jj1tteaktf0zd0anm8854
```

## 7. Atualização do plugin

Para atualizar o plugin após modificações:

1. Faça as alterações no código
2. Commit as mudanças no Git
3. Compile novamente:
   ```bash
   bash prepare.sh && npm run build
   ```
4. Publique a nova versão:
   ```bash
   xtp plugin push
   ```

O sistema criará automaticamente uma nova versão do plugin.

## 8. Integração com MCP.run

Depois de publicado, seu plugin estará disponível no MCP.run através de diferentes tipos de URLs e integrações.

### 8.1 Conexão via SSE (Server-Sent Events)

Este é o método padrão para conexão contínua, onde o servidor envia eventos ao cliente:

```
https://www.mcp.run/api/mcp/sse?nonce=XXXXX&username=XXXXX&profile=XXXXX&sig=XXXXX
```

Exemplo prático:

```
https://www.mcp.run/api/mcp/sse?nonce=T8zqU1NRGYjE_eHF3MuT_w&username=diegofornalha&profile=diegofornalha%2Ftess&sig=SBGfKwIDCeuFE52ktYCu5aNI8-LpHyOKB7IIw_BgT44
```

### 8.2 API REST para execução direta de tarefas

Você também pode invocar tarefas diretamente via API REST:

```
https://www.mcp.run/api/runs/USERNAME/PROFILE/TASK?nonce=XXXXX&sig=XXXXX
```

Exemplo prático:

```
https://www.mcp.run/api/runs/diegofornalha/tess/tass?nonce=Zg8Cysug6snMTd20qWE8KA&sig=kq4EXU6dtydmIpyO7KjhDOmGckG77XHG__t9POLvs3k
```

Uso com curl:

```bash
curl -X POST "https://www.mcp.run/api/runs/diegofornalha/tess/tass?nonce=Zg8Cysug6snMTd20qWE8KA&sig=kq4EXU6dtydmIpyO7KjhDOmGckG77XHG__t9POLvs3k" \
  -H "Content-Type: application/json" \
  -d '{"input": "Listar todos os agentes disponíveis"}'
```

## 9. Configurando tarefas no MCP.run

O MCP.run permite criar tarefas personalizadas que utilizam as ferramentas do seu plugin.

### 9.1 Criando uma nova tarefa

1. Acesse o painel do MCP.run: https://www.mcp.run/settings/
2. Navegue até "Tasks" em seu perfil (ex: diegofornalha/tess)
3. Clique em "New Task" para criar uma tarefa

### 9.2 Configurando o prompt da tarefa

Ao criar uma tarefa, forneça instruções específicas no prompt. Exemplo:

```
Você é um assistente especializado em gerenciar agentes TESS. Sua tarefa é ajudar o usuário a:
1. Listar os agentes disponíveis
2. Executar agentes quando solicitado
3. Gerenciar arquivos associados aos agentes

Use as ferramentas da API TESS para realizar essas tarefas e responda sempre em português.
```

### 9.3 Acessando a tarefa configurada

Após configurar a tarefa, você pode acessá-la através de:

1. **Interface web**: https://www.mcp.run/settings/tasks/diegofornalha/tess/NOME_DA_TAREFA
2. **API REST**: https://www.mcp.run/api/runs/diegofornalha/tess/NOME_DA_TAREFA?nonce=XXX&sig=XXX
3. **Cliente SSE**: Através da URL SSE do seu perfil

## 10. Integração com Arcee CLI

Você pode integrar as ferramentas TESS ao seu Arcee CLI para uso direto em aplicações Python.

### 10.1 Configuração da integração

1. Configure a URL SSE no arquivo `.env` do Arcee CLI:
   ```
   MCP_SSE_URL=https://www.mcp.run/api/mcp/sse?nonce=T8zqU1NRGYjE_eHF3MuT_w&username=diegofornalha&profile=diegofornalha%2Ftess&sig=SBGfKwIDCeuFE52ktYCu5aNI8-LpHyOKB7IIw_BgT44
   ```

2. Crie um módulo de integração em `arcee_cli/examples/mcp/tess_integration.py`

3. Implemente funções para processar comandos TESS, com manipuladores para:
   - Listar agentes
   - Obter detalhes de agentes
   - Executar agentes
   - Gerenciar arquivos

4. Registre os comandos no cliente de chat:
   ```python
   # Em arcee_cli/chat/__init__.py
   from arcee_cli.examples.mcp.tess_integration import register_tess_commands
   
   # No inicializador
   register_tess_commands(chat_client)
   ```

### 10.2 Uso via Arcee CLI

Após a integração, você pode usar comandos como:

```
/tess.listar_agentes page=1 per_page=10
/tess.obter_agente agent_id=42
/tess.executar_agente agent_id=42 model="tess-ai-light"
/tess.help
```

## 11. Entendendo o SSE (Server-Sent Events)

O SSE é uma tecnologia fundamental no MCP.run que permite comunicação unidirecional do servidor para o cliente.

### 11.1 Características do SSE

- Conexão HTTP persistente unidirecional (servidor → cliente)
- Formato de texto simples e leve
- Reconexão automática em caso de falha
- Ideal para atualizações em tempo real

### 11.2 Implementação no código

O Arcee CLI já possui uma implementação robusta de cliente SSE em:
`arcee_cli/infrastructure/mcp/mcp_sse_client.py`

Este cliente gerencia:
- Conexão e reconexão
- Processamento de eventos
- Filas de eventos
- Manipulação de erros

### 11.3 Fluxo SSE com TESS

1. O cliente conecta ao endpoint SSE do MCP.run
2. O cliente envia solicitações de ferramentas TESS
3. O servidor processa as solicitações e retorna eventos com resultados
4. O cliente processa os eventos e exibe resultados

## 12. Resolução de problemas

### Erros comuns

1. **Erro de autenticação:**
   ```
   Error: "GET extension-points/ext_01je4jj1tteaktf0zd0anm8854" HTTP ERROR 401
   ```
   Solução: Execute `xtp login` novamente ou verifique seu token XTP.

2. **Erro de compilação:**
   ```
   Error: error generating plugin: dependency is not available: extism-py
   ```
   Solução: Execute `bash prepare.sh` para instalar as dependências.

3. **Erro de publicação:**
   ```
   Error: Failed to push plugin: ...
   ```
   Solução: Verifique se o plugin compilou corretamente e se você tem permissões.

4. **Tarefa não configurada no MCP.run:**
   ```
   I apologize, but I notice that this appears to be an example/template task prompt...
   ```
   Solução: Configure o prompt específico para a tarefa nas configurações.

5. **Erro de conexão SSE:**
   ```
   Falha na conexão SSE: HTTP 401
   ```
   Solução: Verifique se a URL SSE está atualizada e contém os parâmetros de autenticação corretos.

## 13. Recursos adicionais

- [Documentação do XTP](https://xtp.dylibso.com/docs)
- [Repositório GitHub do plugin](https://github.com/diegofornalha/mcp-server-tess-xtp)
- [API TESS](https://tess.pareto.io/api)
- [MCP.run](https://www.mcp.run)
- [Documentação MCP SSE](https://www.mcp.run/docs/sse)
- [Repositório Arcee CLI](https://github.com/diegofornalha/arcee-cli)

---

Este guia é mantido por Diego Fornalha. Para dúvidas ou sugestões, abra uma issue no GitHub. 