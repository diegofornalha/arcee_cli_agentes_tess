# Consulta Dinâmica à API TESS: Melhores Práticas

## Visão Geral

Implementamos uma abordagem dinâmica para consulta de agentes na API TESS, eliminando a necessidade de manter listas estáticas de agentes no código. Esta abordagem traz diversos benefícios:

1. **Dados sempre atualizados**: Consultas em tempo real garantem informações precisas
2. **Código mais limpo**: Eliminação de hardcoding de dados
3. **Manutenção simplificada**: Não é necessário atualizar o código quando novos agentes são adicionados
4. **Flexibilidade**: Suporte automático a novos parâmetros e campos de resposta

## Implementação Passo a Passo

### 1. Configuração do Cliente HTTP

```python
import requests
import os
import logging

# Obter credenciais do ambiente
api_key = os.getenv("TESS_API_KEY")
if not api_key:
    return "❌ ERRO: Chave API do TESS não encontrada nas variáveis de ambiente."

# Configuração da requisição
url = 'https://tess.pareto.io/api/agents'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Parâmetros de paginação
params = {
    'page': 1,
    'per_page': 30  # Ajuste conforme necessário
}
```

### 2. Execução da Requisição

```python
try:
    logging.info('Realizando requisição para listar agentes TESS...')
    
    # Fazer a requisição
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()  # Levanta exceção para erros HTTP
    
    # Processar a resposta
    data = response.json()
    agentes = data.get('data', [])
    total = data.get('total', 0)
    
except requests.exceptions.RequestException as e:
    logging.error(f"Erro ao listar agentes TESS: {e}")
    return f"❌ Erro ao listar agentes: {str(e)}"
```

### 3. Filtragem Dinâmica (para busca)

Para buscar agentes por termo, implementamos uma filtragem dinâmica no lado do cliente:

```python
# Filtrar agentes que correspondem ao termo de busca
resultados = []
for agente in agentes:
    titulo = agente.get('title', '').lower()
    descricao = agente.get('description', '').lower()
    
    if termo.lower() in titulo or termo.lower() in descricao:
        resultados.append(agente)
```

### 4. Formatação da Resposta

```python
# Formatar a resposta
if not agentes:
    return "🔍 Nenhum agente disponível no momento."

resposta = f"📋 Lista de agentes disponíveis (Total: {total}):\n\n"

for i, agente in enumerate(agentes, 1):
    resposta += f"{i}. {agente.get('title', 'Sem título')}\n"
    resposta += f"   ID: {agente.get('id', 'N/A')}\n"
    resposta += f"   Slug: {agente.get('slug', 'N/A')}\n"
    resposta += f"   Descrição: {agente.get('description', 'Sem descrição')}\n\n"
```

## Comparação com a Abordagem Anterior

### Antes: Listas Hardcoded

```python
# Lista estática de agentes
agentes_info = [
    {
        "id": "53", 
        "slug": "e-mail-de-venda-Sxtjz8",
        "titulo": "E-mail de Venda",
        "descricao": "Cria um e-mail persuasivo para vender produtos ou serviços destacando diferenciais."
    },
    {
        "id": "52", 
        "slug": "titulo-de-email-para-anuncio-de-novo-recurso-fDba8a",
        "titulo": "Título de E-mail para Anúncio de Novo Recurso",
        "descricao": "Gera títulos chamativos para e-mails anunciando novos recursos de produtos."
    },
    # ... mais agentes ...
]
```

### Depois: Consulta Dinâmica

```python
# Configuração da requisição
url = 'https://tess.pareto.io/api/agents'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Obter dados em tempo real
response = requests.get(url, headers=headers, params=params, timeout=30)
agentes = response.json().get('data', [])
```

## Boas Práticas para Manter o Código Limpo

1. **Centralização de Configurações**: Mantenha URLs, endpoints e parâmetros padrão em um arquivo de configuração separado

2. **Tratamento de Erros Robusto**: Implemente tratamento de exceções abrangente para garantir resiliência

3. **Cache Inteligente**: Implemente um sistema de cache com invalidação por tempo para reduzir chamadas à API:

```python
CACHE_TTL = 300  # 5 minutos

def get_agents_with_cache():
    cache_key = "tess_agents"
    current_time = time.time()
    
    # Verificar cache
    if cache_key in self.cache:
        cache_time, cache_data = self.cache[cache_key]
        if current_time - cache_time < CACHE_TTL:
            return cache_data
    
    # Consultar API
    data = fetch_agents_from_api()
    
    # Atualizar cache
    self.cache[cache_key] = (current_time, data)
    
    return data
```

4. **Abstração em Camadas**: Separe o código em:
   - Camada de Serviço: Responsável pelas chamadas à API
   - Camada de Negócios: Processamento, filtragem e lógica 
   - Camada de Apresentação: Formatação das respostas para o usuário

5. **Paginação Eficiente**: Implemente paginação do lado do cliente para APIs que já oferecem suporte à paginação do lado do servidor

## Benefícios de Longo Prazo

1. **Escalabilidade**: O sistema se adapta automaticamente quando novos agentes são adicionados à plataforma TESS

2. **Manutenção Reduzida**: Eliminação de atualizações manuais de código quando o catálogo de agentes muda

3. **Resiliência**: Tratamento adequado de erros e situações de indisponibilidade da API

4. **Adaptabilidade**: Facilidade para suportar mudanças na API, como novos campos ou formatos de resposta

## Conclusão

A implementação de uma abordagem dinâmica para consumo de APIs, eliminando dados hardcoded, representa uma melhoria significativa na qualidade e manutenibilidade do código. Seguindo este padrão, garantimos que o sistema se mantenha atualizado com os recursos mais recentes da API TESS sem necessidade de intervenção manual.

Esta abordagem segue os princípios de Clean Code e DRY (Don't Repeat Yourself), contribuindo para um codebase mais limpo e sustentável no longo prazo. 