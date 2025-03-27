#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Provedor de serviços do Arcee AI
"""

import os
import time
import json
import logging
from typing import Dict, List, Tuple, Union, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
from rich import print

from ..logging_config import obter_logger, configurar_loggers_bibliotecas

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do logger
logger = obter_logger("arcee_provider")

# Garantir que os loggers de bibliotecas estão configurados
configurar_loggers_bibliotecas()

class ArceeProvider:
    """Provedor de serviços do Arcee AI"""

    def __init__(self):
        """Inicializa o provedor"""
        # Carrega variáveis de ambiente
        load_dotenv()

        # INVERSÃO DE PRIORIDADE: Agora prioriza a configuração sobre as variáveis de ambiente
        # Primeiro tenta carregar do arquivo de configuração
        self.api_key = self._load_api_key_from_config()

        # Se não encontrou na configuração, tenta das variáveis de ambiente
        if not self.api_key:
            self.api_key = os.getenv("ARCEE_API_KEY")

        if not self.api_key:
            raise ValueError(
                "API key não encontrada. Defina ARCEE_API_KEY no .env ou configure com 'arcee configure'."
            )

        self.model = os.getenv("ARCEE_MODEL") or "auto"
        
        # Rastreamento de modelos
        self.last_model_used = None
        self.model_usage_stats = {}

        # Templates de mensagem do sistema para diferentes contextos
        self.system_templates = {
            "default": "Você deve sempre responder em português do Brasil. Use uma linguagem natural e informal, mas profissional. Suas respostas devem ser claras, objetivas e culturalmente adequadas para o Brasil.",
            "technical": "Você deve sempre responder em português do Brasil. Para questões técnicas, forneça explicações detalhadas com exemplos práticos quando possível. Mantenha uma linguagem técnica apropriada.",
            "creative": "Você deve sempre responder em português do Brasil. Para tarefas criativas, seja imaginativo e ofereça múltiplas opções. Use uma linguagem expressiva e envolvente."
        }

    
        # Configura o cliente OpenAI
        self.client = OpenAI(
            api_key=self.api_key, 
            base_url="https://models.arcee.ai/v1",
        )

    def _load_api_key_from_config(self) -> str:
        """Carrega a chave API do arquivo de configuração"""
        config_file = os.path.expanduser("~/.arcee/config.json")
        if not os.path.exists(config_file):
            return ""

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("api_key", "")
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {str(e)}")
            return ""
            
    def _select_system_template(self, messages: List[Dict[str, str]]) -> str:
        """
        Seleciona o template de sistema mais adequado com base nas mensagens
        
        Args:
            messages: Lista de mensagens da conversa
            
        Returns:
            Conteúdo do template de sistema selecionado
        """
        # Verifica últimas mensagens do usuário para entender o contexto
        last_user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "").lower()
                break
        
        
        # Se não identificar um contexto específico, usa o template padrão
        return self.system_templates["default"]

    def health_check(self) -> Tuple[bool, str]:
        """Verifica a saúde da API"""
        try:
            # Apenas verifica se temos uma chave API configurada
            if not self.api_key:
                return False, "Chave API não configurada"
            return True, "Chave API está configurada"
        except Exception as e:
            logger.error(f"Erro ao verificar configuração: {str(e)}")
            return False, f"Erro ao verificar configuração: {str(e)}"

    def generate_content_chat(
        self, messages: List[Dict[str, str]]
    ) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """Gera conteúdo usando o chat com seleção automática de modelo e template"""
        try:
            if not self.api_key:
                return {"error": "Chave API não configurada"}

            # Registra apenas o tempo inicial sem exibir mensagem
            start_time = time.time()
            
            # Seleciona o template de sistema apropriado com base no contexto
            system_content = self._select_system_template(messages)
            
            # Cria uma cópia das mensagens para não modificar a original
            processed_messages = messages.copy()
            
            # Adiciona ou atualiza a mensagem do sistema
            if not processed_messages or processed_messages[0].get("role") != "system":
                processed_messages = [{"role": "system", "content": system_content}] + processed_messages
            else:
                # Atualiza a mensagem de sistema existente
                processed_messages[0]["content"] = system_content

            # Parâmetros adicionais para o modo auto
            extra_params = {}
            if self.model == "auto":
                # Pode incluir parâmetros específicos para o modo auto
                # como solicitação de metadados sobre o modelo selecionado
                extra_params = {}
                logger.info("Usando modo AUTO para seleção dinâmica de modelo")

            # Faz a requisição usando o cliente OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=processed_messages,
                temperature=0.7,
                **extra_params
            )

            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.debug(f"Tempo de resposta da API: {elapsed_time:.2f} segundos")

            # Processa e retorna a resposta
            return self._process_response(response)

        except Exception as e:
            logger.error(f"Erro na chamada à API da Arcee: {e}")
            return {"error": str(e)}

    def _process_response(self, response) -> Dict[str, Any]:
        """
        Processa a resposta da API da Arcee

        Args:
            response: Resposta do cliente OpenAI

        Returns:
            Dict[str, Any]: Resposta processada
        """
        try:
            # Extrai o texto da resposta
            content = response.choices[0].message.content

            # Obtém metadados da resposta
            finish_reason = response.choices[0].finish_reason
            model_used = response.model
            
            # Rastreia o modelo usado para análise e ajustes futuros
            self.last_model_used = model_used
            
            # Atualiza estatísticas de uso do modelo
            if model_used in self.model_usage_stats:
                self.model_usage_stats[model_used] += 1
            else:
                self.model_usage_stats[model_used] = 1
                
            # Log do modelo selecionado para depuração
            if self.model == "auto":
                logger.info(f"Modo AUTO selecionou o modelo: {model_used}")

            # Formata a resposta
            processed_response = {
                "text": content,
                "finish_reason": finish_reason,
                "model": model_used,
                "selected_model": model_used,
                "raw_response": response,
            }

            return processed_response

        except Exception as e:
            logger.error(f"Erro ao processar resposta da Arcee: {e}")
            return {
                "text": "",
                "error": f"Falha ao processar resposta: {str(e)}",
                "raw_response": response,
            }

    def chat(self, mensagem: str, historico: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Processa uma mensagem de chat e retorna a resposta

        Args:
            mensagem: Mensagem do usuário
            historico: Histórico de mensagens anteriores

        Returns:
            Dict[str, Any]: Resposta da IA com metadados
        """
        try:
            # Inicializa o histórico se não fornecido
            if historico is None:
                historico = []

            # Adiciona a mensagem atual ao histórico
            mensagens = historico + [{"role": "user", "content": mensagem}]

            # Gera a resposta
            resposta = self.generate_content_chat(mensagens)

            if "error" in resposta:
                return {
                    "text": f"❌ Erro: {resposta['error']}",
                    "error": resposta["error"]
                }

            # Retorna a resposta com metadados
            return {
                "text": resposta["text"],
                "model": resposta.get("selected_model", "desconhecido"),
                "finish_reason": resposta.get("finish_reason", ""),
                "metadata": {
                    "model_usage_stats": self.model_usage_stats
                }
            }

        except Exception as e:
            logger.error(f"Erro no processamento do chat: {str(e)}")
            return {
                "text": f"❌ Erro: {str(e)}",
                "error": str(e)
            }
