#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import json
import subprocess
import time
from dotenv import load_dotenv

from mcp import StdioServerParameters

# Carregar variáveis de ambiente
load_dotenv()

async def test_mcp_connection():
    """Testa se o servidor MCP do Databutton pode ser inicializado."""
    
    # Verificar se a variável de ambiente necessária está configurada
    databutton_api_key = os.getenv("DATABUTTON_API_KEY")
    if not databutton_api_key:
        print("Erro: DATABUTTON_API_KEY não está configurada")
        print("Configure-a no arquivo .env ou exporte-a no terminal")
        return
    
    # Imprimir a chave mascarada para debug
    masked_key = databutton_api_key[:8] + "..." + databutton_api_key[-4:] if len(databutton_api_key) > 12 else "***"
    print(f"Testando com DATABUTTON_API_KEY: {masked_key}")
    
    # Iniciar o servidor MCP como um processo separado
    try:
        # Primeiro verificar se o comando existe
        try:
            result = subprocess.run(
                ["which", "databutton-app-mcp"],
                capture_output=True,
                text=True,
                check=True
            )
            databutton_path = result.stdout.strip()
            print(f"Caminho do databutton-app-mcp: {databutton_path}")
        except subprocess.CalledProcessError:
            print("Erro: Comando 'databutton-app-mcp' não encontrado")
            return
        
        # Preparar o ambiente para o subprocesso
        env = os.environ.copy()
        env["DATABUTTON_API_KEY"] = databutton_api_key
        
        # Iniciar o processo
        print("Iniciando o servidor MCP como processo separado...")
        process = subprocess.Popen(
            [databutton_path],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"Servidor MCP iniciado com PID: {process.pid}")
        
        # Aguardar um pouco para permitir que o servidor inicialize
        print("Aguardando inicialização do servidor...")
        time.sleep(3)
        
        # Verificar se o processo ainda está em execução
        if process.poll() is None:
            print("Servidor MCP está rodando!")
            print("Executando por 5 segundos para verificar estabilidade...")
            
            # Aguardar alguns segundos para verificar a estabilidade
            for i in range(5):
                if process.poll() is not None:
                    print(f"Servidor encerrou com código: {process.poll()}")
                    break
                print(f"Aguardando... {i+1}/5")
                time.sleep(1)
            
            if process.poll() is None:
                print("Servidor MCP estável por 5 segundos!")
                print("O teste foi bem-sucedido!")
                
                # Encerrar o processo graciosamente
                print("Encerrando o servidor MCP...")
                process.terminate()
                
                # Esperar até 5 segundos pelo encerramento
                for _ in range(10):
                    if process.poll() is not None:
                        break
                    time.sleep(0.5)
                
                # Se ainda estiver em execução, forçar encerramento
                if process.poll() is None:
                    print("Forçando encerramento...")
                    process.kill()
                
                return_code = process.wait()
                print(f"Servidor MCP encerrado com código: {return_code}")
            else:
                print("O servidor MCP encerrou prematuramente.")
        else:
            print(f"Erro: O servidor MCP não iniciou corretamente. Código de saída: {process.poll()}")
            stdout, stderr = process.communicate()
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
    
    except Exception as e:
        print(f"Erro ao testar o servidor MCP: {e}")
        import traceback
        traceback.print_exc()

# Ponto de entrada
if __name__ == "__main__":
    print("Iniciando teste do servidor MCP...")
    asyncio.run(test_mcp_connection())
    print("Teste finalizado") 