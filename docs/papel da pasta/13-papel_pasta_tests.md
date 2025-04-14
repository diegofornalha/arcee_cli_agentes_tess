# Documentação da Pasta `tests`

## Visão Geral

A pasta `tests` contém scripts e utilitários de teste que permitem avaliar o funcionamento dos diferentes componentes do projeto Arcee CLI, com foco especial na integração com a API TESS. Estes testes não são testes unitários automatizados tradicionais, mas sim scripts de diagnóstico e validação que podem ser executados manualmente para verificar a funcionalidade e conectividade do sistema.

## Propósito

O propósito principal desta pasta é:

1. **Validação da API TESS**: Fornecer ferramentas para testar a conectividade e funcionalidade da API TESS.
2. **Diagnóstico de Problemas**: Ajudar a identificar e diagnosticar problemas de integração.
3. **Demonstração de Uso**: Servir como exemplos práticos de como utilizar os componentes do sistema.
4. **Verificação de Implantação**: Permitir a validação rápida após implantações ou configurações.

## Componentes Principais

### 1. `test_api_tess.py`

Este é o script de teste mais completo, que implementa diversas funcionalidades para interagir com a API TESS:

- **Listar Agentes**: Função `listar_agentes` que obtém e exibe a lista de agentes disponíveis no TESS.
- **Executar Agente**: Função `executar_agente` que envia uma mensagem para um agente TESS e obtém a resposta.
- **Suporte a Diferentes Identificadores**: Capacidade de identificar agentes por ID, slug ou palavras-chave no título.
- **Modos de Execução**: Suporte para execução CLI (interativa) ou como biblioteca.
- **Filtragem de Agentes**: Funcionalidades para filtrar agentes por tipo ou palavra-chave.
- **Logging Detalhado**: Sistema de logging configurável para depuração.

### 2. `test_tess_provider.py`

Script focado no teste do provedor TESS, que encapsula a comunicação com a API:

- **Teste de Conexão**: Verifica se a conexão com a API TESS pode ser estabelecida.
- **Listagem de Agentes**: Obtém e exibe a lista de agentes disponíveis.
- **Detalhes de Agente**: Recupera informações detalhadas sobre um agente específico.
- **Feedback Visual**: Utiliza a biblioteca `rich` para exibir resultados formatados no terminal.

### 3. `test_tess_cli.py`

Script para testar a interface de linha de comando integrada com a API TESS:

- **Listagem de Agentes via CLI**: Executa o comando do Arcee CLI para listar agentes.
- **Detalhes de Agente via CLI**: Obtém detalhes de um agente específico através do CLI.
- **Chat com Agente**: Testa a funcionalidade de chat interativo com um agente TESS.
- **Verificação de Ambiente**: Verifica se as variáveis de ambiente necessárias estão configuradas.

### 4. `test_tess_url.py`

Script especializado em testar a execução de agentes TESS a partir de URLs:

- **Parsing de URL**: Função `parse_tess_url` para extrair slug do agente e parâmetros de uma URL TESS.
- **Execução de Agente por URL**: Permite executar um agente especificado por uma URL TESS completa.
- **Suporte a Parâmetros de URL**: Extrai e utiliza parâmetros como temperatura e modelo da URL.
- **Diagnóstico Detalhado**: Exibe informações detalhadas para diagnóstico em caso de falha.

## Uso Prático

Os scripts da pasta `tests` podem ser executados individualmente a partir da linha de comando:

```bash
# Teste básico do provedor TESS
python -m tests.test_tess_provider

# Teste de execução de agente específico
python -m tests.test_api_tess executar <ID_OU_SLUG> "Sua mensagem aqui"

# Teste de listagem de agentes
python -m tests.test_api_tess listar

# Teste de URL TESS
python -m tests.test_tess_url "@https://agno.pareto.io/pt-BR/dashboard/user/ai/chat/ai-chat/professional-dev-ai?temperature=0.7"
```

## Integração com o Projeto

Estes scripts de teste se integram com o restante do projeto da seguinte forma:

1. **Uso de Componentes Reais**: Utilizam os mesmos componentes (providers, tools) que são utilizados na aplicação principal.
2. **Configuração Compartilhada**: Compartilham a mesma configuração (.env) utilizada pela aplicação.
3. **Diagnóstico de Ponta a Ponta**: Testam o fluxo completo desde a configuração até a interação com a API.

## Estado Atual e Recomendações

O estado atual da pasta `tests` é funcional, mas apresenta algumas limitações:

1. **Ausência de Testes Unitários**: Os scripts atuais são principalmente testes de integração/funcionais, faltando testes unitários automatizados.
2. **Limitada Cobertura de Código**: Os testes não cobrem todos os componentes do sistema.
3. **Sem Framework de Testes**: Não utiliza um framework de testes padrão (como pytest).

Recomendações para evolução:

1. **Implementar Testes Unitários**: Adicionar testes unitários para componentes críticos.
2. **Adotar pytest**: Migrar para um framework de testes reconhecido como o pytest.
3. **Implementar Testes de Regressão**: Desenvolver testes automatizados que possam ser executados para garantir que novas mudanças não quebrem funcionalidades existentes.
4. **Melhorar Cobertura**: Expandir os testes para cobrir mais componentes e cenários.

## Conclusão

A pasta `tests` fornece ferramentas valiosas para diagnóstico e validação manual da integração com a API TESS, permitindo verificar rapidamente se o sistema está configurado corretamente e se os componentes estão funcionando conforme esperado. Embora não substitua testes unitários automatizados tradicionais, esses scripts são úteis durante o desenvolvimento e depuração, facilitando a identificação e resolução de problemas de integração. 