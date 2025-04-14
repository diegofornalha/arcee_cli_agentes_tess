#!/usr/bin/env python3
import requests

# Token de acesso para a API TESS (token de exemplo, não use em produção)
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c2VyXzEyMzQ1Njc4OTAiLCJpYXQiOjE3MTUxMDU5MzAsImV4cCI6MTcxNTcxMDczMH0.aBcDeFgHiJkLmNoPqRsTuVwXyZ"

# URL para a API TESS - listar agentes com paginação
url = "https://agno.pareto.io/api/agents?page=1&per_page=10"

# Configuração de headers com autenticação Bearer
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
print(f"Status code: {response.status_code}")
print(f"Response content: {response.text}")

if response.status_code == 200:
    data = response.json()
    agents = data.get("data", [])
    print(f"\nVocê tem {len(agents)} agentes disponíveis:")
    for i, agent in enumerate(agents, 1):
        print(f"{i}. {agent.get('title')} (ID: {agent.get('id')})")
else:
    print(f"Erro ao consultar os agentes: {response.text}")