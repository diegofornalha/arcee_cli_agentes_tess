# Uso do comando uvx para Databutton MCP

## Instalação
O comando `uvx` foi configurado como um wrapper para `uv tool run`, permitindo executar ferramentas Python em ambientes efêmeros.

## Como usar
Para executar o Databutton Model Context Protocol (MCP), use o seguinte comando:

```bash
# Ative o ambiente virtual primeiro
source venv/bin/activate

# Execute o databutton-app-mcp com sua API key
DATABUTTON_API_KEY=sua_api_key uvx databutton-app-mcp@latest
```

## Opções disponíveis
O comando suporta as seguintes opções:

```
-k APIKEYFILE, --apikeyfile APIKEYFILE  Arquivo contendo a API key
-v, --verbose                           Executar em modo verbose com logs de informação
-d, --debug                             Executar em modo muito verbose com logs de debug
--show-uri                              Mostrar URI que seria conectada e sair
-u URI, --uri URI                       Usar uma URI personalizada para o endpoint do servidor MCP
```

## Observações
- Em vez de fornecer um arquivo de API key com -k, você pode definir a variável de ambiente DATABUTTON_API_KEY.
- Acesse https://databutton.com para criar aplicativos e obter sua API key.
