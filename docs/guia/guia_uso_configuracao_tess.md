# Guia de Uso e Configuração - TESS API

Este documento unifica todas as informações sobre como usar e configurar a API TESS, incluindo comandos disponíveis, modelos suportados e configurações para ambiente local e remoto.

## Índice

1. [Comandos TESS Disponíveis](#comandos-tess-disponíveis)
2. [Modelos TESS e Como Selecioná-los](#modelos-tess-e-como-selecioná-los)
3. [Consulta Dinâmica à API](#consulta-dinâmica-à-api)
4. [Servidor TESS Local](#servidor-tess-local)
5. [Exemplos Práticos](#exemplos-práticos)

---

## Comandos TESS Disponíveis

### Comandos Simplificados (Recomendados)

Estes são os comandos mais simples e recomendados para uso no chat Arcee:

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `executar <id-do-agente> "<mensagem>"` | Executa um agente específico | `executar professional-dev-ai "Como implementar um singleton em Python?"` |
| `listar agentes` | Lista todos os agentes disponíveis | `listar agentes` |
| `listar agentes chat` | Lista apenas agentes do tipo chat | `listar agentes chat` |
| `agentes <palavra-chave>` | Busca agentes com uma palavra-chave | `agentes linkedin` |

### Comandos via Chat (Alternativos)

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `executar agente <id> com mensagem "<texto>"` | Executa um agente específico | `executar agente professional-dev-ai com mensagem "Como implementar um singleton em Python?"` |
| `buscar agentes tess para <termo>` | Busca agentes por tema | `buscar agentes tess para email` |
| `buscar agentes tipo chat para <termo>` | Busca agentes do tipo chat por tema | `buscar agentes tipo chat para linkedin` |
| `transformar texto em post para linkedin: <texto>` | Atalho para criar um post para LinkedIn | `transformar texto em post para linkedin: Lançamento do produto X` |
| `criar email de venda para: <produto>` | Atalho para gerar um email de vendas | `criar email de venda para: software de gestão` |

### Comandos via Linha de Comando

Estes comandos podem ser executados diretamente pelo terminal:

```bash
# Listar todos os agentes
python -m tests.test_api_tess listar

# Listar agentes de chat
python -m tests.test_api_tess listar-chat

# Listar agentes por palavra-chave
python -m tests.test_api_tess listar-keyword linkedin

# Executar um agente específico
python -m tests.test_api_tess executar professional-dev-ai "Como implementar um singleton em Python?"
```

### Usando URLs do TESS

Você pode especificar um modelo diretamente através de uma URL do TESS, que pode ser inserida no chat do Arcee:

```
@https://tess.pareto.io/pt-BR/dashboard/user/ai/chat/ai-chat/professional-dev-ai?temperature=0&model=claude-3-7-sonnet-latest-thinking&tools=no-tools#
```

Parâmetros importantes na URL:
- `model`: O modelo a ser utilizado
- `temperature`: Controla a aleatoriedade (0-1, onde 0 é mais determinístico)
- `tools`: Habilita ou desabilita ferramentas ("internet", "no-tools", etc.)

---

## Modelos TESS e Como Selecioná-los

### Modelos Disponíveis

| Modelo | Descrição | Características |
|--------|-----------|----------------|
| `claude-3-7-sonnet-latest` | Versão padrão do Claude 3.7 Sonnet | Alta qualidade de resposta, raciocínio lógico avançado, suporte a ferramentas |
| `claude-3-7-sonnet-latest-thinking` | Versão do Claude 3.7 com modo de pensamento | Mostra o raciocínio passo a passo, ideal para problemas complexos |
| `tess-5-pro` | Modelo padrão para agentes de chat | Bom equilíbrio entre velocidade e qualidade |
| `tess-ai-light` | Modelo leve para tarefas simples | Resposta rápida, ideal para tarefas diretas |

### Modelos de Pensamento (Thinking)

Os modelos com `-thinking` no nome são projetados para mostrar o processo de raciocínio passo a passo. Eles são especialmente úteis para:

- Resolução de problemas matemáticos
- Análise lógica
- Desenvolvimento de algoritmos
- Tarefas de programação
- Qualquer situação onde o processo de raciocínio é tão importante quanto a resposta final

### Recomendações de Uso

- **Para problemas matemáticos ou lógicos complexos**: Use `claude-3-7-sonnet-latest-thinking`
- **Para programação e desenvolvimento**: Use `claude-3-7-sonnet-latest` com ferramentas habilitadas
- **Para tarefas criativas**: Use modelos com temperature mais alta (0.7-1.0)
- **Para respostas precisas e determinísticas**: Use temperature baixa (0-0.3)
- **Para uso geral**: Confie no modo AUTO do Arcee

### Modo AUTO do Arcee

O modo AUTO do Arcee seleciona automaticamente o modelo mais adequado com base no contexto da sua mensagem:

- Para iniciar o chat no modo AUTO: `arcee chat`
- Para ver estatísticas dos modelos usados: digite `modelos` no chat
- O sistema escolhe entre diferentes modelos dependendo da complexidade e tipo da sua consulta

---

## Consulta Dinâmica à API

### Visão Geral da Abordagem

Implementamos uma abordagem dinâmica para consulta de agentes na API TESS, eliminando a necessidade de manter listas estáticas de agentes no código. Esta abordagem traz diversos benefícios:

1. **Dados sempre atualizados**: Consultas em tempo real garantem informações precisas
2. **Código mais limpo**: Eliminação de hardcoding de dados
3. **Manutenção simplificada**: Não é necessário atualizar o código quando novos agentes são adicionados
4. **Flexibilidade**: Suporte automático a novos parâmetros e campos de resposta

### Como Funciona

#### 1. Consulta à API para identificação de agentes

```python
def executar_agente(agent_id, mensagem, is_cli=True, specific_params=None):
    # ...
    # Se não é um ID numérico, vamos buscar na API
    if not agent_id.isdigit():
        # Buscar de forma dinâmica na API
        try:
            success, data = listar_agentes(is_cli=False)
            if success:
                encontrado = False
                for agent in data.get('data', []):
                    # Verificar se bate com o slug ou contém o ID fornecido
                    if (agent.get('slug') == agent_id or 
                        agent.get('slug', '').startswith(agent_id) or 
                        agent.get('slug', '').endswith(agent_id) or 
                        agent_id in agent.get('slug', '')):
                        id_numerico = agent.get('id')
                        tipo_agente = agent.get('type', '')
                        encontrado = True
                        break
                    # Verificar também pelo título para maior flexibilidade
                    elif agent_id.lower() in agent.get('title', '').lower():
                        id_numerico = agent.get('id')
                        tipo_agente = agent.get('type', '')
                        encontrado = True
                        break
```

#### 2. Configuração automática com base no tipo

```python
# Determinar se o agente é do tipo chat
is_chat_agent = False

# Verificar se é um agente de chat com base no tipo ou no ID
if ((tipo_agente and tipo_agente.lower() == "chat") or
    agent_id.lower().startswith("chat-") or 
    agent_id == "chat" or 
    agent_id == "professional-dev-ai" or 
    id_numerico == "3238"):
    is_chat_agent = True
    
# Configurar parâmetros com base no tipo de agente
if is_chat_agent:
    # Parâmetros para agentes do tipo chat
    modelo = "tess-5-pro"
    temperatura = "0.5"
    ferramentas = "no-tools"
    
    # Configurações específicas baseadas no agente
    if agent_id == "professional-dev-ai" or id_numerico == "3238":
        modelo = "claude-3-7-sonnet-latest"
        temperatura = "0"
        ferramentas = "internet"
```

### Vantagens da Consulta Dinâmica

1. **Agentes são consultados em tempo real** na API
2. **Qualquer agente disponível** no TESS pode ser utilizado imediatamente
3. **Nenhuma manutenção necessária** para novos agentes
4. **Suporte a comandos diretos** como `executar professional-dev-ai "Pergunta?"`
5. **Detecção automática** do tipo de agente e configuração de parâmetros adequados

---

## Servidor TESS Local

### Visão Geral da Solução

A implementação do servidor TESS local consiste em:

1. **Servidor TESS Local**: Um servidor HTTP simples em Node.js que simula a API TESS
2. **Provider do Cliente**: Uma classe que se comunica com o servidor local ou remoto
3. **Interface de Chat**: A CLI existente que utiliza o provider para conversar com o usuário

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

### Provider do Cliente

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

### Configuração do Ambiente

Para configurar o sistema, adicione as seguintes variáveis de ambiente:

```
# .env
TESS_API_KEY=your_api_key_here
TESS_API_URL=https://tess.pareto.io/api
TESS_LOCAL_SERVER_URL=http://localhost:3000
USE_LOCAL_TESS=True
```

### Como Executar

#### 1. Iniciar o Servidor TESS Local

```bash
./scripts/start_tess_server_background.sh
```

#### 2. Verificar Funcionamento

```bash
curl http://localhost:3000/health
```

#### 3. Executar o Chat

```bash
python -m src chat
```

---

## Exemplos Práticos

### Exemplo 1: Encontrar um Agente para Posts de LinkedIn

```
agentes linkedin
```

Resultado:
```
Encontrados 3 agentes relacionados a "linkedin":

1. Transformar Texto em Post para LinkedIn
   ID: 67
   Slug: transformar-texto-em-post-para-linkedin-mF37hV
   Descrição: Transforma um texto bruto em um post otimizado para LinkedIn

2. Gerador de Hashtags para LinkedIn
   ID: 892
   Slug: gerador-de-hashtags-para-linkedin-xKt567
   Descrição: Cria hashtags relevantes para seus posts no LinkedIn

3. Analista de Perfil LinkedIn
   ID: 1204
   Slug: analista-de-perfil-linkedin-YuN982
   Descrição: Analisa e sugere melhorias para seu perfil no LinkedIn
```

### Exemplo 2: Usar o Claude 3.7 Sonnet para Programação

```
@https://tess.pareto.io/pt-BR/dashboard/user/ai/chat/ai-chat/professional-dev-ai?temperature=0&model=claude-3-7-sonnet-latest&tools=internet# "Escreva um algoritmo em Python para encontrar números primos até 100"
```

Resultado:
```python
def encontrar_primos_ate_n(n):
    """
    Encontra todos os números primos até n usando o Crivo de Eratóstenes
    
    Args:
        n: O limite superior até onde procurar primos
        
    Returns:
        Uma lista com todos os números primos até n
    """
    # Inicialmente, considere que todos os números são primos
    eh_primo = [True for i in range(n+1)]
    p = 2
    
    # Verifique todos os números até a raiz quadrada de n
    while p * p <= n:
        # Se p for primo, marque seus múltiplos como não primos
        if eh_primo[p]:
            for i in range(p * p, n+1, p):
                eh_primo[i] = False
        p += 1
    
    # Gere a lista de números primos
    primos = []
    for p in range(2, n+1):
        if eh_primo[p]:
            primos.append(p)
    
    return primos

# Encontrar e imprimir todos os primos até 100
primos_ate_100 = encontrar_primos_ate_n(100)
print(f"Números primos até 100: {primos_ate_100}")
print(f"Total de primos encontrados: {len(primos_ate_100)}")
```

### Exemplo 3: Criar Email de Vendas Rapidamente

```
criar email de venda para: software de gestão de projetos
```

Resultado:
```
Assunto: Transforme o Gerenciamento de Projetos da Sua Empresa com Nossa Solução Inovadora

Prezado(a) Gestor(a),

Espero que esteja bem.

Você já parou para calcular quanto tempo e recursos sua equipe perde com gerenciamento manual de projetos, planilhas desatualizadas e comunicação fragmentada?

Apresentamos o [Nome do Software], uma solução completa de gestão de projetos desenvolvida especificamente para empresas que buscam:

✅ Reduzir em até 40% o tempo gasto em tarefas administrativas
✅ Centralizar toda comunicação e documentação em um único ambiente
✅ Acompanhar em tempo real o progresso de todos os projetos
✅ Automatizar relatórios e análises de desempenho
✅ Integrar com as ferramentas que você já utiliza

Nossa plataforma já ajudou mais de 500 empresas a aumentar sua produtividade em média 35% nos primeiros 60 dias de uso.

Gostaria de conhecer como podemos ajudar sua empresa especificamente? Tenho disponibilidade para uma demonstração personalizada esta semana, onde poderei mostrar como nosso software se adapta perfeitamente às necessidades do seu negócio.

Que tal uma conversa de 20 minutos para explorarmos as possibilidades?

Aguardo seu retorno.

Atenciosamente,

[Seu Nome]
[Sua Posição]
[Telefone de Contato]
[Email]
```

### Exemplo 4: Executar Multi-Chat para Pensamento Complexo

```
executar multi-chat-S7C0WU "Explique a teoria da relatividade geral em termos simples, usando analogias"
```

Resultado:
```
A Teoria da Relatividade Geral de Einstein, explicada de forma simples:

Imagine o espaço-tempo como um grande colchão elástico esticado. Quando não há nada sobre ele, o colchão é plano - isto representa o espaço vazio.

Agora, coloque uma bola de boliche (representando uma estrela ou planeta) no meio do colchão. A bola afunda, criando uma depressão no tecido. Esta é a maneira de Einstein visualizar como a massa curva o espaço-tempo ao seu redor.

Se você rolar uma bolinha de gude (representando um objeto menor, como um planeta ou cometa) perto da bola de boliche, ela não seguirá em linha reta. Em vez disso, seguirá um caminho curvo, possivelmente orbitando a bola de boliche antes de cair na depressão. Einstein nos mostrou que os planetas não orbitam o Sol por causa de uma "força" invisível puxando-os, mas porque seguem o caminho mais reto possível através de um espaço-tempo que foi curvado pelo Sol.

Outra analogia: imagine dirigir em linha reta no Equador. Se você continuar dirigindo "em linha reta", eventualmente voltará ao ponto de partida, tendo feito um círculo completo ao redor da Terra. Isso não é porque você virou o volante, mas porque a superfície da Terra é curva. Da mesma forma, a luz das estrelas distantes parece curvar-se ao redor do Sol não porque existe uma força puxando-a, mas porque está seguindo o caminho mais reto possível através de um espaço-tempo que foi curvado pela massa do Sol.

A beleza da Relatividade Geral é que ela reinterpreta a gravidade não como uma força, mas como um efeito geométrico - a curvatura do próprio espaço-tempo causada pela presença de massa e energia.
```

## Comandos Úteis no Arcee Chat

- `ajuda`: Mostra a lista de comandos disponíveis
- `limpar`: Limpa o histórico da conversa
- `sair`: Encerra o chat
- `modelos`: Mostra estatísticas dos modelos usados no modo AUTO
- `listar agentes`: Lista todos os agentes TESS disponíveis
- `executar <id> "<mensagem>"`: Executa um agente TESS específico

## Solução de Problemas Comuns

### Erro "Comando não implementado"

Se você receber a mensagem "Comando não implementado", verifique:

1. Se está usando a sintaxe correta conforme este documento
2. Se o comando está entre os suportados
3. Se o módulo MCPNLProcessor foi carregado corretamente (verifique logs)

### Erro ao Executar Agentes

O erro `UnboundLocalError: cannot access local variable` foi resolvido com a inicialização correta das variáveis globais.

### Erro de Chave API

Se receber erro relacionado à chave API não encontrada:

```bash
# Configure a variável de ambiente
export TESS_API_KEY="sua-chave-api-aqui"
```

### Agente Não Encontrado

Se um agente não for encontrado:

1. Verifique se o ID ou slug está correto usando o comando `listar agentes`
2. Confirme o acesso à API com sua chave
3. Tente usar o ID numérico se estiver usando slug 