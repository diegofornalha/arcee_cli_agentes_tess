require('dotenv').config();
const express = require('express');
const cors = require('cors');
const extism = require('@extism/extism');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3000;
const PLUGIN_PATH = path.join(__dirname, 'target/wasm32-wasip1/release/mcp_server_tess_xtp.wasm');

let plugin = null;

async function initPlugin() {
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
}

// Função para processar requisições através do plugin
async function handlePluginRequest(req) {
    const request = {
        method: req.method,
        path: req.path,
        body: JSON.stringify(req.body),
        query: req.query,
        headers: req.headers
    };
    
    const result = await plugin.call('handle_request', JSON.stringify(request));
    // Converter DataView para string e depois fazer parse como JSON
    const resultString = new TextDecoder().decode(result);
    return JSON.parse(resultString);
}

// Health check
app.get('/health', async (req, res) => {
    try {
        const response = await handlePluginRequest(req);
        res.status(response.status).json(JSON.parse(response.body));
    } catch (error) {
        console.error('Health check error:', error);
        res.status(500).json({ error: 'Erro interno do servidor' });
    }
});

// Listar ferramentas MCP
app.get('/api/mcp/tools', async (req, res) => {
    try {
        const response = await handlePluginRequest(req);
        res.status(response.status)
           .set(response.headers)
           .send(response.body);
    } catch (error) {
        console.error('MCP tools error:', error);
        res.status(500).json({ error: 'Erro ao listar ferramentas MCP' });
    }
});

// Executar ferramenta MCP
app.post('/api/mcp/execute', async (req, res) => {
    try {
        const response = await handlePluginRequest(req);
        res.status(response.status)
           .set(response.headers)
           .send(response.body);
    } catch (error) {
        console.error('MCP execute error:', error);
        res.status(500).json({ error: 'Erro ao executar ferramenta MCP' });
    }
});

// Inicializar plugin e iniciar servidor
async function start() {
    try {
        await initPlugin();
        app.listen(PORT, () => {
            console.log(`Servidor TESS rodando na porta ${PORT}`);
        });
    } catch (error) {
        console.error('Erro ao inicializar servidor:', error);
        process.exit(1);
    }
}

start(); 