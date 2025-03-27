# Modelos TESS Disponíveis e Como Selecioná-los no Arcee Chat

## Introdução

O TESS (Task and Event Simple System) é uma plataforma que oferece acesso a diversos modelos de IA para processamento de linguagem natural, incluindo várias versões do Claude da Anthropic. O Arcee Chat proporciona uma interface para interagir com esses modelos através de comandos simples e naturais.

Este guia explica os diferentes modelos disponíveis no TESS e como selecioná-los através do Arcee Chat.

## Modelos Disponíveis

### Modelos Principais

| Modelo | Descrição | Características |
|--------|-----------|----------------|
| `claude-3-7-sonnet-latest` | Versão padrão do Claude 3.7 Sonnet | Alta qualidade de resposta, raciocínio lógico avançado, suporte a ferramentas |
| `claude-3-7-sonnet-latest-thinking` | Versão do Claude 3.7 com modo de pensamento | Mostra o raciocínio passo a passo, ideal para problemas complexos |
| `tess-5-pro` | Modelo padrão para agentes de chat | Bom equilíbrio entre velocidade e qualidade |
| `tess-ai-light` | Modelo leve para tarefas simples | Resposta rápida, ideal para tarefas diretas |

### Modelos de Pensamento (Thinking)

Os modelos com `-thinking` no nome (como `claude-3-7-sonnet-latest-thinking`) são projetados para mostrar o processo de raciocínio passo a passo. Eles são especialmente úteis para:

- Resolução de problemas matemáticos
- Análise lógica
- Desenvolvimento de algoritmos
- Tarefas de programação
- Qualquer situação onde o processo de raciocínio é tão importante quanto a resposta final

## Métodos de Seleção de Modelos

### 1. Usando URLs do TESS

Você pode especificar um modelo diretamente através de uma URL do TESS, que pode ser inserida no chat do Arcee:

```
@https://tess.pareto.io/pt-BR/dashboard/user/ai/chat/ai-chat/professional-dev-ai?temperature=0&model=claude-3-7-sonnet-latest-thinking&tools=no-tools#
```

Parâmetros importantes:
- `model`: O modelo a ser utilizado
- `temperature`: Controla a aleatoriedade (0-1, onde 0 é mais determinístico)
- `tools`: Habilita ou desabilita ferramentas ("internet", "no-tools", etc.)

### 2. Usando a Linha de Comando

Para testar modelos específicos via linha de comando:

```bash
python -m tests.test_api_tess executar professional-dev-ai "Sua mensagem aqui"
```

Para o modo de pensamento:

```bash
python test_tess_url.py '@https://tess.pareto.io/pt-BR/dashboard/user/ai/chat/ai-chat/professional-dev-ai?temperature=0&model=claude-3-7-sonnet-latest-thinking&tools=no-tools#' "Sua mensagem aqui"
```

### 3. Usando o Chat do Arcee

No chat do Arcee, você pode:

- Usar o modo AUTO (padrão), que seleciona automaticamente o melhor modelo
- Ver estatísticas de uso de modelos com o comando `modelos`
- Executar agentes TESS específicos com o comando:
  ```
  test_api_tess executar <id-agente> <mensagem>
  ```

## Exemplos Práticos

### Usando o Claude 3.7 Sonnet com Thinking para Problemas Complexos

```
@https://tess.pareto.io/pt-BR/dashboard/user/ai/chat/ai-chat/multi-chat-S7C0WU?temperature=1&model=claude-3-7-sonnet-latest-thinking&tools=no-tools# "Resolva o seguinte problema matemático passo a passo..."
```

### Usando o Claude 3.7 Sonnet para Programação

```
@https://tess.pareto.io/pt-BR/dashboard/user/ai/chat/ai-chat/professional-dev-ai?temperature=0&model=claude-3-7-sonnet-latest&tools=internet# "Escreva um algoritmo em Python para..."
```

### Usando o TESS-5-Pro para Tarefas Gerais

```
test_api_tess executar chat "Como posso melhorar minha produtividade no trabalho?"
```

## Modo AUTO do Arcee

O modo AUTO do Arcee seleciona automaticamente o modelo mais adequado com base no contexto da sua mensagem:

- Para iniciar o chat no modo AUTO: `arcee chat`
- Para ver estatísticas dos modelos usados: digite `modelos` no chat
- O sistema escolhe entre diferentes modelos dependendo da complexidade e tipo da sua consulta

## Recomendações de Uso

- **Para problemas matemáticos ou lógicos complexos**: Use `claude-3-7-sonnet-latest-thinking`
- **Para programação e desenvolvimento**: Use `claude-3-7-sonnet-latest` com ferramentas habilitadas
- **Para tarefas criativas**: Use modelos com temperature mais alta (0.7-1.0)
- **Para respostas precisas e determinísticas**: Use temperature baixa (0-0.3)
- **Para uso geral**: Confie no modo AUTO do Arcee

## Comandos Úteis no Arcee Chat

- `ajuda`: Mostra a lista de comandos disponíveis
- `limpar`: Limpa o histórico da conversa
- `sair`: Encerra o chat
- `modelos`: Mostra estatísticas dos modelos usados no modo AUTO
- `test_api_tess listar`: Lista todos os agentes TESS disponíveis
- `test_api_tess executar <id> <mensagem>`: Executa um agente TESS específico 