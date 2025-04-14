import asyncio
import json
import os
import traceback
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

import httpx
from agno.models.base import Model
from agno.models.message import Message
from agno.models.response import ModelResponse, ModelResponseEvent
from dotenv import load_dotenv
from openai import OpenAI
from openai import AsyncOpenAI

# Carregar variáveis de ambiente
load_dotenv()

class ArceeModel(Model):
    """
    Modelo para integração com a API da Arcee.
    
    Esta classe implementa todos os métodos necessários para integrar
    a API da Arcee com o framework Agno, baseando-se na implementação
    do projeto arcee_cli_agentes_tess.
    """
    
    def __init__(
        self,
        id: str = None,
        model: str = None,
        api_url: str = None,
        api_key: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        timeout: float = 60.0,
        debug: bool = True,
        **kwargs
    ):
        """
        Inicializa o modelo Arcee.
        
        Args:
            id: ID do modelo (default: "arcee-{model}")
            model: Nome do modelo Arcee a ser usado (default: obtido de ARCEE_MODEL)
            api_url: URL da API Arcee (default: obtido de ARCEE_APP_URL)
            api_key: Chave de API para a Arcee (default: obtido de ARCEE_API_KEY)
            temperature: Temperatura para geração de texto (0.0 a 1.0)
            max_tokens: Número máximo de tokens a serem gerados
            timeout: Tempo limite para requisições à API (em segundos)
            debug: Se True, imprime mensagens de debug
            **kwargs: Argumentos adicionais para configuração
        """
        try:
            # Obter valores de variáveis de ambiente
            self.model = model or os.getenv("ARCEE_MODEL", "auto")
            self.api_url = api_url or os.getenv("ARCEE_APP_URL", "https://models.arcee.ai/v1")
            self.api_key = api_key or os.getenv("ARCEE_API_KEY")
            self.temperature = temperature
            self.max_tokens = max_tokens
            self.timeout = timeout
            self.debug = debug
            self.extra_config = kwargs
            
            # Definir o ID do modelo se não foi fornecido
            model_id = id or f"arcee-{self.model}"
            
            # Chamar o construtor da classe base com o ID do modelo
            super().__init__(id=model_id)
            
            if self.debug:
                print(f"Inicializando modelo Arcee com os seguintes parâmetros:")
                print(f"  - ID: {model_id}")
                print(f"  - URL: {self.api_url}")
                print(f"  - Modelo: {self.model}")
                print(f"  - Temperatura: {self.temperature}")
                print(f"  - Max tokens: {self.max_tokens}")
            
            # Verificar se as credenciais estão disponíveis
            if not self.api_key:
                raise ValueError("API key da Arcee não fornecida. Defina a variável de ambiente ARCEE_API_KEY ou forneça a chave diretamente.")
            
            if not self.api_url:
                raise ValueError("URL da API Arcee não fornecida. Defina a variável de ambiente ARCEE_APP_URL ou forneça a URL diretamente.")
                
            # Inicializar os clientes OpenAI (síncrono e assíncrono)
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_url,
                timeout=self.timeout
            )
            
            self.async_client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.api_url,
                timeout=self.timeout
            )
            
            # Estatísticas de uso de modelos
            self.last_model_used = None
            self.model_usage_stats = {}
                
        except Exception as e:
            print(f"Erro ao inicializar modelo Arcee: {e}")
            print(traceback.format_exc())
            raise
    
    def _prepare_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """
        Converte mensagens do formato Agno para o formato esperado pela API da Arcee.
        
        Args:
            messages: Lista de mensagens no formato Agno
            
        Returns:
            Lista de mensagens no formato esperado pela API da Arcee
        """
        try:
            arcee_messages = []

            # Verifica se há uma mensagem do sistema no início
            has_system = False
            if messages and messages[0].role == "system":
                has_system = True
            
            # Se não tiver mensagem do sistema, adiciona uma mensagem padrão em português
            if not has_system:
                arcee_messages.append({
                    "role": "system",
                    "content": "Você deve sempre responder em português do Brasil. Use uma linguagem natural e informal, mas profissional. Suas respostas devem ser claras, objetivas e culturalmente adequadas para o Brasil."
                })
            
            # Processa cada mensagem
            for message in messages:
                role = message.role
                content = message.content
                
                # Adaptação da estrutura para o formato da Arcee
                arcee_message = {
                    "role": role,
                    "content": content
                }
                
                arcee_messages.append(arcee_message)
            
            if self.debug:
                print(f"Mensagens convertidas para formato da Arcee: {json.dumps(arcee_messages)}")
                
            return arcee_messages
        except Exception as e:
            print(f"Erro ao preparar mensagens para API da Arcee: {e}")
            print(traceback.format_exc())
            # Em caso de erro, retornar uma mensagem simples
            return [{"role": "user", "content": "Olá, você pode me ajudar?"}]
    
    def invoke(self, messages: List[Message], **kwargs) -> str:
        """
        Invoca o modelo Arcee de forma síncrona.
        
        Args:
            messages: Lista de mensagens
            **kwargs: Parâmetros adicionais
            
        Returns:
            Texto de resposta do modelo
        """
        try:
            if self.debug:
                print(f"Invocando modelo Arcee de forma síncrona")
            
            # Converte as mensagens para o formato da OpenAI
            processed_messages = self._prepare_messages(messages)
            
            # Parâmetros adicionais para personalizar a requisição
            params = {
                "model": kwargs.get("model", self.model),
                "messages": processed_messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            }
            
            # Adicionar quaisquer parâmetros extras
            for k, v in self.extra_config.items():
                if k not in params:
                    params[k] = v
            
            # Realiza a chamada à API
            response = self.client.chat.completions.create(**params)
            
            # Rastreia o modelo usado
            model_used = response.model
            self.last_model_used = model_used
            
            # Atualiza estatísticas de uso do modelo
            if model_used in self.model_usage_stats:
                self.model_usage_stats[model_used] += 1
            else:
                self.model_usage_stats[model_used] = 1
                
            # Extrai o conteúdo da resposta
            content = response.choices[0].message.content
            
            if self.debug:
                print(f"Resposta recebida do modelo {model_used}: {content[:100]}...")
                
            return content
            
        except Exception as e:
            print(f"Erro ao invocar modelo Arcee de forma síncrona: {e}")
            print(traceback.format_exc())
            return f"Ocorreu um erro ao invocar o modelo Arcee: {str(e)}"
    
    async def ainvoke(self, messages: List[Message], **kwargs) -> str:
        """
        Invoca o modelo Arcee de forma assíncrona.
        
        Args:
            messages: Lista de mensagens
            **kwargs: Parâmetros adicionais
            
        Returns:
            Texto de resposta do modelo
        """
        try:
            if self.debug:
                print(f"Invocando modelo Arcee de forma assíncrona")
            
            # Converte as mensagens para o formato da OpenAI
            processed_messages = self._prepare_messages(messages)
            
            # Parâmetros adicionais para personalizar a requisição
            params = {
                "model": kwargs.get("model", self.model),
                "messages": processed_messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            }
            
            # Adicionar quaisquer parâmetros extras
            for k, v in self.extra_config.items():
                if k not in params:
                    params[k] = v
            
            # Realiza a chamada à API
            response = await self.async_client.chat.completions.create(**params)
            
            # Rastreia o modelo usado
            model_used = response.model
            self.last_model_used = model_used
            
            # Atualiza estatísticas de uso do modelo
            if model_used in self.model_usage_stats:
                self.model_usage_stats[model_used] += 1
            else:
                self.model_usage_stats[model_used] = 1
                
            # Extrai o conteúdo da resposta
            content = response.choices[0].message.content
            
            if self.debug:
                print(f"Resposta assíncrona recebida do modelo {model_used}: {content[:100]}...")
                
            return content
            
        except Exception as e:
            print(f"Erro ao invocar modelo Arcee de forma assíncrona: {e}")
            print(traceback.format_exc())
            return f"Ocorreu um erro ao comunicar com a API da Arcee: {str(e)}"
    
    def invoke_stream(self, messages: List[Message], **kwargs) -> AsyncGenerator[str, None]:
        """
        Invoca o modelo Arcee de forma síncrona com streaming.
        Usa a versão assíncrona internamente.
        
        Args:
            messages: Lista de mensagens
            **kwargs: Parâmetros adicionais
            
        Returns:
            Gerador que produz partes da resposta
        """
        async def _stream_wrapper():
            try:
                async for chunk in self.ainvoke_stream(messages, **kwargs):
                    yield chunk
            except Exception as e:
                print(f"Erro no stream wrapper: {e}")
                print(traceback.format_exc())
                yield f"Erro no streaming: {str(e)}"

        return _stream_wrapper()
    
    async def ainvoke_stream(self, messages: List[Message], **kwargs) -> AsyncGenerator[str, None]:
        """
        Invoca o modelo Arcee de forma assíncrona com streaming.
        
        Args:
            messages: Lista de mensagens
            **kwargs: Parâmetros adicionais
            
        Yields:
            Partes da resposta à medida que são geradas
        """
        try:
            if self.debug:
                print(f"Invocando modelo Arcee com streaming")
            
            # Converte as mensagens para o formato da OpenAI
            processed_messages = self._prepare_messages(messages)
            
            # Parâmetros adicionais para personalizar a requisição
            params = {
                "model": kwargs.get("model", self.model),
                "messages": processed_messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "stream": True
            }
            
            # Adicionar quaisquer parâmetros extras
            for k, v in self.extra_config.items():
                if k not in params:
                    params[k] = v
            
            # Realiza a chamada à API com streaming
            stream = await self.async_client.chat.completions.create(**params)
            
            # Rastreia o modelo usado (será atualizado quando o streaming terminar)
            model_used = None
            
            # Processa a resposta em streaming
            async for chunk in stream:
                if not model_used and hasattr(chunk, 'model'):
                    model_used = chunk.model
                    if self.debug:
                        print(f"Stream usando modelo: {model_used}")
                
                # Extrai o conteúdo delta
                if hasattr(chunk, 'choices') and chunk.choices is not None and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        yield delta.content
            
            # Atualiza estatísticas do modelo no final do streaming
            if model_used:
                self.last_model_used = model_used
                if model_used in self.model_usage_stats:
                    self.model_usage_stats[model_used] += 1
                else:
                    self.model_usage_stats[model_used] = 1
                    
        except Exception as e:
            print(f"Erro ao chamar API da Arcee em modo streaming: {e}")
            print(traceback.format_exc())
            yield f"Ocorreu um erro ao comunicar com a API da Arcee: {str(e)}"
    
    def parse_provider_response(self, response: Dict[str, Any]) -> ModelResponse:
        """
        Analisa a resposta da API da Arcee para o formato do Agno.
        
        Args:
            response: Resposta da API da Arcee
            
        Returns:
            Resposta no formato do Agno
        """
        try:
            if self.debug:
                print(f"Analisando resposta da API: {json.dumps(response) if isinstance(response, dict) else str(response)}")
                
            # Obtém o conteúdo com base no tipo de resposta
            content = ""
            if isinstance(response, dict):
                content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            elif hasattr(response, 'choices') and len(response.choices) > 0:
                content = response.choices[0].message.content
            else:
                content = str(response)
            
            return ModelResponse(
                content=content,
                message_data={"content": content, "role": "assistant"}
            )
        except Exception as e:
            print(f"Erro ao analisar resposta da API: {e}")
            print(traceback.format_exc())
            return ModelResponse(
                content=f"Erro ao analisar resposta: {str(e)}",
                message_data={"content": f"Erro ao analisar resposta: {str(e)}", "role": "assistant"}
            )
    
    def parse_provider_response_delta(self, delta: Dict[str, Any]) -> ModelResponse:
        """
        Analisa um delta de resposta da API da Arcee para o formato do Agno.
        
        Args:
            delta: Delta de resposta da API da Arcee
            
        Returns:
            Resposta no formato do Agno
        """
        try:
            if self.debug:
                print(f"Analisando delta de resposta: {json.dumps(delta) if isinstance(delta, dict) else str(delta)}")
                
            # Obtém o conteúdo com base no tipo de delta
            content = ""
            if isinstance(delta, dict):
                content = delta.get("choices", [{}])[0].get("delta", {}).get("content", "")
            elif hasattr(delta, 'choices') and len(delta.choices) > 0:
                content = delta.choices[0].delta.content or ""
            else:
                content = str(delta)
            
            # Criar um ModelResponse em vez de um ModelResponseEvent
            return ModelResponse(
                content=content,
                event=ModelResponseEvent.assistant_response
            )
        except Exception as e:
            print(f"Erro ao analisar delta de resposta da API: {e}")
            print(traceback.format_exc())
            # Criar um ModelResponse em vez de um ModelResponseEvent
            return ModelResponse(
                content=f"Erro ao analisar delta: {str(e)}",
                event=ModelResponseEvent.assistant_response
            ) 