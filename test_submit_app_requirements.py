#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import json
import subprocess
import time
from dotenv import load_dotenv

# Importar o modelo Arcee
sys.path.append('/home/agentsai')
from arcee_cli_agentes_tess.arcee_model import ArceeModel

# Carregar variáveis de ambiente
load_dotenv()

# Definir dados de exemplo para a submissão
SAMPLE_APP_REQUIREMENTS = {
    "name": "Meu App Teste",
    "pitch": "Um aplicativo para testar a ferramenta submit_app_requirements",
    "spec": {
        "description": "Este é um aplicativo de teste para verificar se a ferramenta MCP está funcionando corretamente. O aplicativo servirá para validar a integração entre o modelo Arcee e o Databutton MCP.",
        "targetAudience": "Desenvolvedores e testadores que estão tentando usar o MCP",
        "design": "Design minimalista com cores claras e interface intuitiva",
        "typography": "Fonte sans-serif para fácil leitura em todas as plataformas"
    }
}

async def test_submit_app_requirements():
    """Testa a ferramenta submit_app_requirements do MCP usando uma implementação direta."""
    
    # Verificar se as variáveis de ambiente necessárias estão configuradas
    databutton_api_key = os.getenv("DATABUTTON_API_KEY")
    if not databutton_api_key:
        print("Erro: DATABUTTON_API_KEY não está configurada")
        return
    
    # Preparar o ambiente para o subprocesso
    env = os.environ.copy()
    env["DATABUTTON_API_KEY"] = databutton_api_key
    
    # Verificar se o comando existe
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
    
    # Preparar o conteúdo JSON para enviar ao processo
    mcp_request = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "runTool",
        "params": {
            "name": "mcp_submit_app_requirements",
            "arguments": SAMPLE_APP_REQUIREMENTS
        }
    }
    
    # Iniciar o processo MCP
    print("Iniciando o servidor MCP...")
    process = subprocess.Popen(
        [databutton_path],
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print(f"Servidor MCP iniciado com PID: {process.pid}")
    
    try:
        # Aguardar um pouco para permitir que o servidor inicialize
        print("Aguardando inicialização do servidor...")
        time.sleep(2)
        
        # Enviar a requisição para o servidor
        print("Enviando requisição para o servidor MCP...")
        request_str = json.dumps(mcp_request) + "\n"
        process.stdin.write(request_str)
        process.stdin.flush()
        
        # Aguardar a resposta (com timeout)
        print("Aguardando resposta...")
        timeout = 10  # segundos
        start_time = time.time()
        
        response_lines = []
        while time.time() - start_time < timeout:
            # Verificar se o processo ainda está em execução
            if process.poll() is not None:
                print(f"Servidor encerrou com código: {process.poll()}")
                break
            
            # Tentar ler uma linha da saída
            line = process.stdout.readline().strip()
            if line:
                response_lines.append(line)
                print(f"Resposta recebida: {line}")
                break
            
            # Pequena pausa para não sobrecarregar a CPU
            time.sleep(0.1)
        
        # Verificar se recebemos alguma resposta
        if response_lines:
            print("Resposta recebida com sucesso!")
            try:
                response = json.loads(response_lines[0])
                print("Resposta JSON:")
                print(json.dumps(response, indent=2))
            except json.JSONDecodeError:
                print(f"Resposta não é um JSON válido: {response_lines[0]}")
        else:
            print("Timeout: Nenhuma resposta recebida do servidor MCP")
            
            # Verificar se há erros
            stderr_output = process.stderr.read()
            if stderr_output:
                print(f"Erros do servidor: {stderr_output}")
    
    except Exception as e:
        print(f"Erro ao chamar a ferramenta: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Encerrar o servidor MCP
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

# Usar o arcee_agno_mcp.py como base para testes mais simples
async def use_arcee_mcp():
    """Usa o script existente arcee_agno_mcp.py para testar a ferramenta."""
    print("Executando o script arcee_agno_mcp.py para testar a ferramenta...")
    
    try:
        # Executar o script existente com uma pergunta específica sobre a ferramenta
        query = "Use a ferramenta submit_app_requirements para enviar os seguintes requisitos de app: nome 'Meu App Teste', pitch 'Um aplicativo para testar a ferramenta', descrição 'Aplicativo de teste para o MCP'"
        
        process = subprocess.Popen(
            ["./run_arcee_mcp.sh", query],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("Aguardando a execução...")
        stdout, stderr = process.communicate()
        
        print("Resultado da execução:")
        print(stdout)
        
        if stderr:
            print("Erros:")
            print(stderr)
    
    except Exception as e:
        print(f"Erro ao executar o script: {e}")
        import traceback
        traceback.print_exc()

# Ponto de entrada
if __name__ == "__main__":
    print("Selecione o método de teste:")
    print("1. Implementação direta (pode não funcionar)")
    print("2. Usar o script existente arcee_agno_mcp.py")
    
    choice = input("Escolha (1 ou 2): ").strip()
    
    if choice == "1":
        print("Iniciando teste direto da ferramenta submit_app_requirements...")
        asyncio.run(test_submit_app_requirements())
    else:
        print("Usando o script existente para testar a ferramenta...")
        asyncio.run(use_arcee_mcp())
    
    print("Teste finalizado") 