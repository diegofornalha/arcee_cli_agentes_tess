#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
from dotenv import load_dotenv
from agno.agent import Agent

# Importar o modelo Arcee
sys.path.append('/home/agentsai')
from arcee_model import ArceeModel

# Carregar variáveis de ambiente
load_dotenv()

async def main():
    """Função principal que cria e executa um agente usando o modelo Arcee via Agno."""
    
    # Verificar se as variáveis de ambiente necessárias estão configuradas
    required_vars = ["ARCEE_API_KEY", "ARCEE_APP_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Erro: As seguintes variáveis de ambiente são necessárias: {', '.join(missing_vars)}")
        print("Por favor, configure-as antes de executar o script.")
        return
    
    try:
        # Inicializar o modelo Arcee
        arcee_model = ArceeModel(
            model=os.getenv("ARCEE_MODEL", "auto"),
            temperature=0.7,
            max_tokens=2000,
            debug=True
        )
        
        print(f"Modelo Arcee inicializado com sucesso.")
        
        # Criar o agente Agno com o modelo Arcee
        agent = Agent(
            model=arcee_model,
            instructions="""
            Você é um assistente de IA que utiliza a API da Arcee, especializada em responder em português do Brasil.
            
            Suas respostas devem ser:
            - Claras e objetivas
            - Culturalmente apropriadas para o contexto brasileiro
            - Bem estruturadas e organizadas
            - Profissionais mas amigáveis
            
            O modelo usado para responder a esta pergunta será selecionado automaticamente pela API da Arcee 
            com base na complexidade e natureza da pergunta.
            """,
            markdown=True,
        )
        
        print("Agente configurado com sucesso.")
        print("\n" + "="*50)
        print("🤖 Assistente Arcee usando framework Agno")
        print("Digite 'sair' para encerrar a conversa.")
        print("="*50 + "\n")
        
        # Loop de chat interativo
        while True:
            user_input = input("👤 Você: ")
            
            if user_input.lower() in ["sair", "exit", "quit"]:
                print("\nEncerrando a conversa. Até mais! 👋")
                break
            
            print("\n🤖 Assistente: ", end="")
            
            # Usar o modo não-streaming para evitar o erro
            try:
                # Primeiro tente com streaming
                stream_success = False
                try:
                    await agent.aprint_response(user_input, stream=True)
                    stream_success = True
                except Exception as e:
                    print(f"\nErro no modo streaming: {e}. Tentando sem streaming...")
                
                # Se o streaming falhar, use o modo normal
                if not stream_success:
                    response = await agent.agenerate_response(user_input)
                    print(response.content)
                
                print("\n")
                
                # Mostrar estatísticas de uso de modelos
                if hasattr(arcee_model, 'last_model_used') and arcee_model.last_model_used:
                    print(f"Modelo usado: {arcee_model.last_model_used}")
            except Exception as e:
                print(f"Erro ao gerar resposta: {e}")
    
    except Exception as e:
        print(f"Erro ao executar o agente: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 