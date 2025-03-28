# Documentação da Pasta `infrastructure`

## Visão Geral

A pasta `infrastructure` é responsável por fornecer componentes de infraestrutura para o Arcee CLI, funcionando como uma camada de abstração que conecta a aplicação com serviços externos, gerencia configurações e implementa recursos técnicos compartilhados. Esta camada segue os princípios da Arquitetura Limpa (Clean Architecture), isolando detalhes de implementação técnica das regras de negócio.

## Propósito

O propósito principal desta pasta é:

1. **Abstração de Serviços Externos**: Encapsular a interação com APIs externas, como TESS e MCP.
2. **Gerenciamento de Configuração**: Prover mecanismos para configuração do sistema.
3. **Logging e Telemetria**: Implementar um sistema unificado de logs para toda a aplicação.
4. **Providers**: Disponibilizar implementações concretas de interfaces definidas na camada de domínio.
5. **Infraestrutura Técnica**: Fornecer componentes compartilhados como clientes HTTP, gerenciamento de cache, e outras utilidades técnicas.

## Estrutura e Componentes

### Componentes Principais

1. **`config.py`**: Gerencia a configuração da aplicação, permitindo salvar e carregar configurações como chaves de API e preferências de organização. Características:
   - Armazenamento de configurações em `~/.arcee/config.json`
   - Interface para configuração interativa via linha de comando
   - Métodos para salvar e carregar configurações

2. **`logging_config.py`**: Implementa um sistema de logging completo e padronizado, oferecendo:
   - Configuração centralizada dos logs da aplicação
   - Suporte para logs em arquivo com rotação (através de `RotatingFileHandler`)
   - Saída rica em console usando `RichHandler`
   - Controle granular de níveis de log para diferentes componentes
   - Supressão de logs desnecessários de bibliotecas externas

3. **Pasta `providers/`**: Contém implementações concretas de serviços externos, incluindo:
   - **`arcee_provider.py`**: Implementação do provider para a API Arcee
   - **`tess_provider.py`**: Implementação do provider para a API TESS, responsável por:
     - Listar e obter detalhes de agentes
     - Executar agentes com parâmetros específicos
     - Verificar a conectividade com a API
   - **`provider_factory.py`**: Factory para criação de providers, facilitando a injeção de dependências

4. **Pasta `mcp/`**: Implementa integração com o protocolo MCP (Model Context Protocol):
   - **`mcp_sse_client.py`**: Cliente para comunicação com servidores MCP via Server-Sent Events (SSE)

5. **Pasta `veyrax/`**: Contém uma implementação de cliente MCP específica para o Veyrax:
   - **`mcp_client.py`**: Cliente MCP para interação com a API Veyrax, permitindo:
     - Listar ferramentas disponíveis
     - Executar ferramentas específicas
     - Gerenciar memórias (salvar, atualizar, listar, excluir)

## Padrões de Design Utilizados

1. **Factory Method**: Implementado em `provider_factory.py` para criar instâncias de providers.
2. **Dependency Injection**: Os providers são injetados nas camadas superiores da aplicação.
3. **Adapter Pattern**: Os providers atuam como adaptadores entre a aplicação e serviços externos.
4. **Singleton**: Padrão aplicado em alguns componentes como a configuração de logging.

## Integração com o Resto do Projeto

A infraestrutura se conecta com as outras camadas da aplicação da seguinte forma:

1. **Domínio**: Implementa interfaces definidas na camada de domínio, respeitando o princípio de inversão de dependência.
2. **Aplicação**: Fornece serviços técnicos para a camada de aplicação, que contém os casos de uso.
3. **Interface**: Apoia a camada de interface do usuário com serviços como logging e configuração.

## Dependências Externas

A pasta `infrastructure` é a principal responsável por gerenciar dependências externas como:

1. Bibliotecas HTTP (`requests`)
2. Gerenciamento de configuração (`json`, arquivos locais)
3. Logging (`logging`, `rich`)
4. Variáveis de ambiente (`dotenv`)

## Estado Atual e Recomendações

A estrutura atual da infraestrutura está bem organizada e segue princípios de arquitetura limpa. No entanto, algumas melhorias poderiam ser consideradas:

1. **Testes Automatizados**: Aumentar a cobertura de testes para os componentes de infraestrutura.
2. **Documentação de API**: Melhorar a documentação das interfaces fornecidas pelos providers.
3. **Abstração Consistente**: Garantir que todos os providers sigam o mesmo padrão de interface.
4. **Tratamento de Erros**: Implementar estratégias mais robustas para tratamento de falhas em serviços externos.
5. **Cache**: Adicionar mecanismos de cache para reduzir chamadas desnecessárias às APIs externas.

## Conclusão

A pasta `infrastructure` desempenha um papel fundamental no projeto Arcee CLI, fornecendo uma camada bem definida de componentes técnicos que isolam detalhes de implementação das regras de negócio. Esta separação clara de responsabilidades facilita a manutenção, testabilidade e evolução da aplicação, permitindo que as camadas de domínio e aplicação se concentrem em expressar as regras de negócio sem preocupações com detalhes técnicos. 