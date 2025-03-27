// Script para testar a API da TESS AI diretamente
const https = require('https');

// Configurações da TESS
const apiKey = 'SUA_TESS_API_KEY'; // Substitua por sua API Key real

// URL da API da TESS
const url = `https://tess.pareto.io/api/agents?page=1&per_page=10`;

console.log(`Consultando agentes disponíveis na TESS AI...`);
console.log(`URL: ${url}\n`);

// Fazer requisição à API da TESS
const options = {
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
  }
};

https.get(url, options, (res) => {
  let data = '';
  
  // Receber dados em chunks
  res.on('data', (chunk) => {
    data += chunk;
  });
  
  // Quando terminar de receber dados
  res.on('end', () => {
    console.log(`Status Code: ${res.statusCode}`);
    
    if (res.statusCode === 200) {
      try {
        // Tentar analisar como JSON
        const response = JSON.parse(data);
        const agents = response.data || [];
        
        console.log(`\nAgentes disponíveis (total: ${agents.length}):`);
        agents.forEach((agent, i) => {
          console.log(`${i+1}. ${agent.title} (ID: ${agent.id})`);
        });
      } catch (e) {
        console.log('Erro ao analisar resposta como JSON:', e.message);
        console.log('Resposta bruta:', data);
      }
    } else {
      console.log(`Erro na requisição: ${res.statusCode}`);
      console.log(`Resposta: ${data}`);
    }
  });
}).on('error', (e) => {
  console.error(`Erro na requisição: ${e.message}`);
}); 