# Implementação de Endpoints MCP em Servidor TESS com Rust: Solução de Problemas

## Introdução

Este documento detalha o processo de solução de problemas encontrados durante a implementação de endpoints MCP (Multi-Channel Platform) no servidor TESS usando Rust e WebAssembly.

## Problemas e Soluções

### 1. Configuração do Ambiente Rust

**Problema:** O ambiente não tinha Rust instalado.

**Solução:**
- Instalamos o Rust usando o script de instalação oficial:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```
- Aplicamos a configuração do ambiente:
```bash
source "$HOME/.cargo/env"
```

### 2. Target WebAssembly Incorreto

**Problema:** O script estava tentando usar `wasm32-wasi` que não estava disponível.

**Solução:**
- Alteramos o target para `wasm32-wasip1` que é o recomendado:
```bash
# No setup.sh
rustup target add wasm32-wasip1
```
- Atualizamos também no package.json:
```json
"build": "cargo build --target wasm32-wasip1 --release"
```

### 3. Limitação de Features do Tokio

**Problema:** Feature `full` do Tokio não é suportada no WebAssembly.

**Solução:**
- Modificamos o Cargo.toml para usar apenas features suportadas em WASM:
```toml
tokio = { version = "1.0", features = ["sync", "macros", "io-util", "rt", "time"] }
```

### 4. Problemas com Tipo de Retorno da Host Function

**Problema:** A função `get_config` tinha tipo de retorno incompatível.

**Solução:**
- Alteramos a assinatura da função host para um tipo compatível:
```rust
#[host_fn]
extern "ExtismHost" {
    fn get_config(key: &str) -> String;
}

fn get_env(key: &str) -> Result<String, Error> {
    let value = unsafe { get_config(key) };
    if value.is_empty() {
        Err(Error::msg(format!("Configuração não encontrada: {}", key)))
    } else {
        Ok(value)
    }
}
```

### 5. Problemas de Lifetime em Valores Temporários

**Problema:** Valores temporários eram descartados enquanto ainda estavam sendo referenciados.

**Solução:**
- Modificamos a estrutura para armazenar adequadamente a string:
```rust
// De
mcp_data.insert("params", &params.to_string());

// Para
mcp_data.insert("session_id", session_id.to_string());
mcp_data.insert("tool", execute_req.tool);
if let Some(params) = execute_req.params {
    mcp_data.insert("params", params.to_string());
}
```

### 6. Integração com a API Extism

**Problema:** A importação e uso da API Extism estavam incorretos.

**Solução:**
- Corrigimos a importação:
```javascript
const extism = require('@extism/extism');
```
- Atualizamos o código para usar a API corretamente:
```javascript
const manifest = {
    wasm: [
        { path: PLUGIN_PATH }
    ],
    config: {
        MCP_API_KEY: process.env.MCP_API_KEY || '',
        MCP_API_URL: process.env.MCP_API_URL || 'https://www.mcp.run/api'
    }
};

plugin = await extism.createPlugin(manifest, { useWasi: true });
```

### 7. Configuração Adequada do Manifesto Extism

**Problema:** O formato do manifesto estava incorreto para o Extism.

**Solução:**
- Adotamos o formato correto usando o caminho do arquivo WASM:
```javascript
const manifest = {
    wasm: [
        { path: PLUGIN_PATH }
    ],
    config: {
        // Configurações aqui
    }
};
```

## Processo de Desenvolvimento

1. **Estrutura do Código Rust**
   - Definimos as estruturas de dados para requisições e respostas
   - Implementamos o handler principal para processar diferentes endpoints

2. **Setup do Ambiente Node.js/Express**
   - Configuramos o servidor Express com CORS e parsing JSON
   - Adicionamos rotas para health check e endpoints MCP

3. **Integração WebAssembly com Node.js**
   - Estabelecemos a comunicação entre Node.js e o código Rust compilado para WebAssembly
   - Implementamos o carregamento do plugin WASM e tratamento de erros

4. **Testes e Depuração**
   - Testamos o endpoint de health check
   - Verificamos a disponibilidade dos endpoints MCP

## Principais Lições Aprendidas

1. **Limitações WebAssembly:** Nem todas as features de bibliotecas Rust são compatíveis com WebAssembly, requerendo configurações específicas.

2. **Gerenciamento de Memória:** O WebAssembly tem um modelo de memória específico que exige atenção especial quanto a lifetimes e ownership.

3. **Comunicação Assíncrona:** É necessário gerenciar corretamente operações assíncronas entre JavaScript e WebAssembly.

4. **Configuração de Manifest:** O formato correto do manifesto é crucial para que o plugin WebAssembly seja carregado corretamente.

5. **Debugging WebAssembly:** Depurar código WebAssembly requer uma abordagem diferente, focando nos logs do lado JavaScript.

## Conclusão

A implementação dos endpoints MCP no servidor TESS usando Rust e WebAssembly foi concluída com sucesso após a resolução dos problemas mencionados. O servidor está agora pronto para ser utilizado, fornecendo uma interface entre aplicações cliente e o serviço MCP.run. 