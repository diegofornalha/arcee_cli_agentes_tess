# Implementação de Chat com Servidor TESS Local

Este documento explica como implementamos o sistema de chat utilizando o servidor TESS local, permitindo testar a aplicação sem depender de serviços externos.

## Visão Geral da Solução

Nossa implementação consiste em três partes principais:

1. **Servidor TESS Local**: Um servidor HTTP simples em Node.js que simula a API TESS
2. **Provider do Cliente**: Uma classe que se comunica com o servidor local ou remoto
3. **Interface de Chat**: A CLI existente que utiliza o provider para conversar com o usuário

## 1. Servidor TESS Local

O servidor local foi implementado como uma aplicação Node.js simples que:

- Fornece um endpoint `/health` para verificação de funcionamento
- Oferece um endpoint `/chat` para processar mensagens de chat
- Simula respostas de um assistente inteligente

### Implementação do Servidor

```javascript
// Principais endpoints
if (req.url === '/health' && req.method === 'GET') {
    // Retorna status do servidor
}

if (req.url === '/chat' && req.method === 'POST') {
    // Processa mensagens de chat
    // Gera respostas baseadas no conteúdo da mensagem
}
```

O servidor inclui uma função `generateResponse()` que:
- Reconhece comandos comuns como "olá", "ajuda", etc.
- Analisa o contexto da conversa
- Fornece respostas personalizadas para tópicos específicos
- Tem respostas genéricas para mensagens não reconhecidas

## 2. Provider do Cliente

Modificamos a classe `TessProvider` para trabalhar tanto com a API TESS oficial quanto com o servidor local:

```python
def __init__(self):
    """Inicializa o provedor TESS com a API key do ambiente."""
    self.api_key = os.getenv("TESS_API_KEY")
    self.api_url = os.getenv("TESS_API_URL", "https://tess.pareto.io/api")
    self.local_server_url = os.getenv("TESS_LOCAL_SERVER_URL", "http://localhost:3000")
    self.use_local_server = os.getenv("USE_LOCAL_TESS", "True").lower() in ("true", "1", "t")
```

O provider verifica a configuração e decide se deve usar o servidor local ou a API remota:

```python
if self.use_local_server:
    # Comunicação com o servidor local
else:
    # Comunicação com a API TESS remota
```

Os métodos principais foram adaptados para funcionar com ambas as opções:
- `health_check()`: Verifica a conexão com o servidor apropriado
- `list_agents()`: Lista agentes disponíveis (simula quando em modo local)
- `get_agent()`: Obtém detalhes de um agente específico
- `execute_agent()`: Executa um agente com parâmetros e mensagens fornecidos

## 3. Configuração do Ambiente

Para configurar o sistema, adicionamos novas variáveis de ambiente:

```
# .env
TESS_API_KEY=your_api_key_here
TESS_API_URL=https://tess.pareto.io/api
TESS_LOCAL_SERVER_URL=http://localhost:3000
USE_LOCAL_TESS=True
```

## Como Executar

### 1. Iniciar o Servidor TESS Local

```bash
./scripts/start_tess_server_background.sh
```

### 2. Verificar Funcionamento

```bash
curl http://localhost:3000/health
```

### 3. Executar o Chat

```bash
python -m src chat
```

## Extensões Futuras

O servidor atual simula respostas básicas, mas pode ser estendido para:

1. **Integração com Modelos Locais**: Adicionar suporte a modelos de linguagem locais como Llama ou similar
2. **Expansão de Funcionalidades**: Implementar mais endpoints para outras funções da API TESS
3. **Persistência de Dados**: Armazenar conversas e configurações em banco de dados local
4. **Interface Web**: Adicionar uma interface web simples para interação além da CLI

---

Esta implementação oferece um ambiente de desenvolvimento isolado e controlado, permitindo testar e desenvolver funcionalidades sem consumir créditos da API TESS remota e sem depender de conectividade internet. 