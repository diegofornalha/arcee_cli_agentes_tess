#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Servidor TESS MCP (Task and Event Simple System) para gerenciamento de tarefas.

Este módulo implementa o servidor da API TESS, que fornece endpoints para o gerenciamento
de quadros, listas e cartões em um sistema simples de gerenciamento de tarefas.
"""

import os
import json
import uuid
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from flask import Flask, request, jsonify, g
from flask_cors import CORS

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Diretório para armazenar os dados
DATA_DIR = os.environ.get("TESS_DATA_DIR", os.path.expanduser("~/.agno"))
BOARDS_FILE = os.path.join(DATA_DIR, "boards.json")

app = Flask(__name__)
CORS(app)

# Middleware para verificar API key, se configurada
@app.before_request
def check_api_key():
    api_key = os.environ.get("TESS_API_KEY")
    if api_key:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer ") or auth_header[7:] != api_key:
            return jsonify({"error": "Acesso não autorizado"}), 401


# Funções auxiliares para gerenciamento de dados
def ensure_data_dir():
    """Garante que o diretório de dados existe"""
    os.makedirs(DATA_DIR, exist_ok=True)


def load_boards() -> Dict[str, Any]:
    """Carrega os dados dos quadros do arquivo"""
    ensure_data_dir()
    if not os.path.exists(BOARDS_FILE):
        return {"boards": {}}
    
    try:
        with open(BOARDS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar dados dos quadros: {str(e)}")
        return {"boards": {}}


def save_boards(data: Dict[str, Any]):
    """Salva os dados dos quadros no arquivo"""
    ensure_data_dir()
    try:
        with open(BOARDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro ao salvar dados dos quadros: {str(e)}")


def get_current_date() -> str:
    """Retorna a data atual no formato ISO"""
    return datetime.datetime.now().isoformat()


# Rotas da API
@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se o servidor está funcionando"""
    return jsonify({"status": "ok"})


@app.route('/api/boards', methods=['GET'])
def get_boards():
    """Retorna todos os quadros"""
    data = load_boards()
    boards_list = []
    
    for board_id, board in data.get("boards", {}).items():
        boards_list.append({
            "id": board_id,
            "name": board.get("name", ""),
            "description": board.get("description", ""),
            "created_at": board.get("created_at", "")
        })
    
    return jsonify({"boards": boards_list})


@app.route('/api/boards/<board_id>', methods=['GET'])
def get_board(board_id):
    """Retorna um quadro específico"""
    data = load_boards()
    board = data.get("boards", {}).get(board_id)
    
    if not board:
        return jsonify({"error": "Quadro não encontrado"}), 404
    
    return jsonify({
        "board": {
            "id": board_id,
            "name": board.get("name", ""),
            "description": board.get("description", ""),
            "created_at": board.get("created_at", ""),
            "lists_order": board.get("lists_order", [])
        }
    })


@app.route('/api/boards', methods=['POST'])
def create_board():
    """Cria um novo quadro"""
    data = load_boards()
    body = request.json
    
    if not body or "name" not in body:
        return jsonify({"error": "Nome do quadro é obrigatório"}), 400
    
    board_id = str(uuid.uuid4())
    created_at = get_current_date()
    
    data.setdefault("boards", {})[board_id] = {
        "name": body.get("name"),
        "description": body.get("description", ""),
        "created_at": created_at,
        "lists": {},
        "lists_order": []
    }
    
    save_boards(data)
    
    return jsonify({
        "board": {
            "id": board_id,
            "name": body.get("name"),
            "description": body.get("description", ""),
            "created_at": created_at
        }
    }), 201


@app.route('/api/boards/<board_id>', methods=['PUT'])
def update_board(board_id):
    """Atualiza um quadro existente"""
    data = load_boards()
    body = request.json
    
    if not data.get("boards", {}).get(board_id):
        return jsonify({"error": "Quadro não encontrado"}), 404
    
    board = data["boards"][board_id]
    
    if "name" in body:
        board["name"] = body["name"]
    if "description" in body:
        board["description"] = body["description"]
    
    save_boards(data)
    
    return jsonify({
        "board": {
            "id": board_id,
            "name": board.get("name", ""),
            "description": board.get("description", ""),
            "created_at": board.get("created_at", "")
        }
    })


@app.route('/api/boards/<board_id>', methods=['DELETE'])
def delete_board(board_id):
    """Exclui um quadro"""
    data = load_boards()
    
    if not data.get("boards", {}).get(board_id):
        return jsonify({"error": "Quadro não encontrado"}), 404
    
    del data["boards"][board_id]
    save_boards(data)
    
    return jsonify({"success": True, "message": "Quadro excluído com sucesso"})


@app.route('/api/boards/<board_id>/lists', methods=['GET'])
def get_lists(board_id):
    """Retorna todas as listas de um quadro"""
    data = load_boards()
    
    if not data.get("boards", {}).get(board_id):
        return jsonify({"error": "Quadro não encontrado"}), 404
    
    board = data["boards"][board_id]
    lists_dict = board.get("lists", {})
    lists_order = board.get("lists_order", [])
    
    # Organiza as listas na ordem definida
    lists = []
    for list_id in lists_order:
        if list_id in lists_dict:
            lists.append({
                "id": list_id,
                "name": lists_dict[list_id].get("name", ""),
                "board_id": board_id,
                "created_at": lists_dict[list_id].get("created_at", "")
            })
    
    # Adiciona listas que não estão na ordem definida
    for list_id, list_data in lists_dict.items():
        if list_id not in lists_order:
            lists.append({
                "id": list_id,
                "name": list_data.get("name", ""),
                "board_id": board_id,
                "created_at": list_data.get("created_at", "")
            })
    
    return jsonify({"lists": lists})


@app.route('/api/lists/<list_id>', methods=['GET'])
def get_list(list_id):
    """Retorna uma lista específica"""
    data = load_boards()
    
    # Procura a lista em todos os quadros
    for board_id, board in data.get("boards", {}).items():
        if list_id in board.get("lists", {}):
            list_data = board["lists"][list_id]
            return jsonify({
                "list": {
                    "id": list_id,
                    "name": list_data.get("name", ""),
                    "board_id": board_id,
                    "created_at": list_data.get("created_at", ""),
                    "cards_order": list_data.get("cards_order", [])
                }
            })
    
    return jsonify({"error": "Lista não encontrada"}), 404


@app.route('/api/boards/<board_id>/lists', methods=['POST'])
def create_list(board_id):
    """Cria uma nova lista em um quadro"""
    data = load_boards()
    body = request.json
    
    if not data.get("boards", {}).get(board_id):
        return jsonify({"error": "Quadro não encontrado"}), 404
    
    if not body or "name" not in body:
        return jsonify({"error": "Nome da lista é obrigatório"}), 400
    
    board = data["boards"][board_id]
    list_id = str(uuid.uuid4())
    created_at = get_current_date()
    
    # Inicializa o dicionário de listas se não existir
    board.setdefault("lists", {})
    board.setdefault("lists_order", [])
    
    board["lists"][list_id] = {
        "name": body.get("name"),
        "created_at": created_at,
        "cards": {},
        "cards_order": []
    }
    
    # Adiciona a nova lista ao final da ordem
    board["lists_order"].append(list_id)
    
    save_boards(data)
    
    return jsonify({
        "list": {
            "id": list_id,
            "name": body.get("name"),
            "board_id": board_id,
            "created_at": created_at
        }
    }), 201


@app.route('/api/lists/<list_id>', methods=['PUT'])
def update_list(list_id):
    """Atualiza uma lista existente"""
    data = load_boards()
    body = request.json
    
    # Procura a lista em todos os quadros
    for board_id, board in data.get("boards", {}).items():
        if list_id in board.get("lists", {}):
            list_data = board["lists"][list_id]
            
            if "name" in body:
                list_data["name"] = body["name"]
            
            # Atualiza a posição da lista, se solicitado
            if "position" in body and isinstance(body["position"], int):
                lists_order = board.get("lists_order", [])
                
                if list_id in lists_order:
                    lists_order.remove(list_id)
                
                position = max(0, min(body["position"], len(lists_order)))
                lists_order.insert(position, list_id)
                board["lists_order"] = lists_order
            
            save_boards(data)
            
            return jsonify({
                "list": {
                    "id": list_id,
                    "name": list_data.get("name", ""),
                    "board_id": board_id,
                    "created_at": list_data.get("created_at", "")
                }
            })
    
    return jsonify({"error": "Lista não encontrada"}), 404


@app.route('/api/lists/<list_id>', methods=['DELETE'])
def delete_list(list_id):
    """Exclui uma lista"""
    data = load_boards()
    
    # Procura a lista em todos os quadros
    for board_id, board in data.get("boards", {}).items():
        if list_id in board.get("lists", {}):
            # Remove a lista do dicionário
            del board["lists"][list_id]
            
            # Remove a lista da ordem
            lists_order = board.get("lists_order", [])
            if list_id in lists_order:
                lists_order.remove(list_id)
            
            save_boards(data)
            return jsonify({"success": True, "message": "Lista excluída com sucesso"})
    
    return jsonify({"error": "Lista não encontrada"}), 404


@app.route('/api/lists/<list_id>/cards', methods=['GET'])
def get_cards(list_id):
    """Retorna todos os cards de uma lista"""
    data = load_boards()
    
    # Procura a lista em todos os quadros
    for board_id, board in data.get("boards", {}).items():
        if list_id in board.get("lists", {}):
            list_data = board["lists"][list_id]
            cards_dict = list_data.get("cards", {})
            cards_order = list_data.get("cards_order", [])
            
            # Organiza os cards na ordem definida
            cards = []
            for card_id in cards_order:
                if card_id in cards_dict:
                    cards.append({
                        "id": card_id,
                        "name": cards_dict[card_id].get("name", ""),
                        "description": cards_dict[card_id].get("description", ""),
                        "due_date": cards_dict[card_id].get("due_date", ""),
                        "list_id": list_id,
                        "board_id": board_id,
                        "created_at": cards_dict[card_id].get("created_at", ""),
                        "archived": cards_dict[card_id].get("archived", False)
                    })
            
            # Adiciona cards que não estão na ordem definida
            for card_id, card_data in cards_dict.items():
                if card_id not in cards_order:
                    cards.append({
                        "id": card_id,
                        "name": card_data.get("name", ""),
                        "description": card_data.get("description", ""),
                        "due_date": card_data.get("due_date", ""),
                        "list_id": list_id,
                        "board_id": board_id,
                        "created_at": card_data.get("created_at", ""),
                        "archived": card_data.get("archived", False)
                    })
            
            return jsonify({"cards": cards})
    
    return jsonify({"error": "Lista não encontrada"}), 404


@app.route('/api/cards/<card_id>', methods=['GET'])
def get_card(card_id):
    """Retorna um card específico"""
    data = load_boards()
    
    # Procura o card em todas as listas de todos os quadros
    for board_id, board in data.get("boards", {}).items():
        for list_id, list_data in board.get("lists", {}).items():
            if card_id in list_data.get("cards", {}):
                card_data = list_data["cards"][card_id]
                return jsonify({
                    "card": {
                        "id": card_id,
                        "name": card_data.get("name", ""),
                        "description": card_data.get("description", ""),
                        "due_date": card_data.get("due_date", ""),
                        "list_id": list_id,
                        "board_id": board_id,
                        "created_at": card_data.get("created_at", ""),
                        "archived": card_data.get("archived", False)
                    }
                })
    
    return jsonify({"error": "Card não encontrado"}), 404


@app.route('/api/lists/<list_id>/cards', methods=['POST'])
def create_card(list_id):
    """Cria um novo card em uma lista"""
    data = load_boards()
    body = request.json
    
    # Procura a lista em todos os quadros
    found = False
    for board_id, board in data.get("boards", {}).items():
        if list_id in board.get("lists", {}):
            found = True
            break
    
    if not found:
        return jsonify({"error": "Lista não encontrada"}), 404
    
    if not body or "name" not in body:
        return jsonify({"error": "Nome do card é obrigatório"}), 400
    
    list_data = board["lists"][list_id]
    card_id = str(uuid.uuid4())
    created_at = get_current_date()
    
    # Inicializa o dicionário de cards se não existir
    list_data.setdefault("cards", {})
    list_data.setdefault("cards_order", [])
    
    list_data["cards"][card_id] = {
        "name": body.get("name"),
        "description": body.get("description", ""),
        "due_date": body.get("due_date", ""),
        "created_at": created_at,
        "archived": False
    }
    
    # Adiciona o novo card ao final da ordem
    list_data["cards_order"].append(card_id)
    
    save_boards(data)
    
    return jsonify({
        "card": {
            "id": card_id,
            "name": body.get("name"),
            "description": body.get("description", ""),
            "due_date": body.get("due_date", ""),
            "list_id": list_id,
            "board_id": board_id,
            "created_at": created_at,
            "archived": False
        }
    }), 201


@app.route('/api/cards/<card_id>', methods=['PUT'])
def update_card(card_id):
    """Atualiza um card existente"""
    data = load_boards()
    body = request.json
    
    # Procura o card em todas as listas de todos os quadros
    for board_id, board in data.get("boards", {}).items():
        for list_id, list_data in board.get("lists", {}).items():
            if card_id in list_data.get("cards", {}):
                card_data = list_data["cards"][card_id]
                
                # Atualiza os campos fornecidos
                for field in ["name", "description", "due_date", "archived"]:
                    if field in body:
                        card_data[field] = body[field]
                
                # Atualiza a posição do card, se solicitado
                if "position" in body and isinstance(body["position"], int):
                    cards_order = list_data.get("cards_order", [])
                    
                    if card_id in cards_order:
                        cards_order.remove(card_id)
                    
                    position = max(0, min(body["position"], len(cards_order)))
                    cards_order.insert(position, card_id)
                    list_data["cards_order"] = cards_order
                
                # Move o card para outra lista, se solicitado
                if "list_id" in body and body["list_id"] != list_id:
                    new_list_id = body["list_id"]
                    found = False
                    
                    # Verifica se a nova lista existe
                    for b_id, b in data.get("boards", {}).items():
                        if new_list_id in b.get("lists", {}):
                            found = True
                            break
                    
                    if found:
                        # Remove o card da lista atual
                        cards_order = list_data.get("cards_order", [])
                        if card_id in cards_order:
                            cards_order.remove(card_id)
                        
                        del list_data["cards"][card_id]
                        
                        # Adiciona o card à nova lista
                        new_list = b["lists"][new_list_id]
                        new_list.setdefault("cards", {})
                        new_list.setdefault("cards_order", [])
                        
                        new_list["cards"][card_id] = card_data
                        new_list["cards_order"].append(card_id)
                        
                        save_boards(data)
                        
                        return jsonify({
                            "card": {
                                "id": card_id,
                                "name": card_data.get("name", ""),
                                "description": card_data.get("description", ""),
                                "due_date": card_data.get("due_date", ""),
                                "list_id": new_list_id,
                                "board_id": b_id,
                                "created_at": card_data.get("created_at", ""),
                                "archived": card_data.get("archived", False)
                            }
                        })
                
                save_boards(data)
                
                return jsonify({
                    "card": {
                        "id": card_id,
                        "name": card_data.get("name", ""),
                        "description": card_data.get("description", ""),
                        "due_date": card_data.get("due_date", ""),
                        "list_id": list_id,
                        "board_id": board_id,
                        "created_at": card_data.get("created_at", ""),
                        "archived": card_data.get("archived", False)
                    }
                })
    
    return jsonify({"error": "Card não encontrado"}), 404


@app.route('/api/cards/<card_id>', methods=['DELETE'])
def delete_card(card_id):
    """Exclui um card"""
    data = load_boards()
    
    # Procura o card em todas as listas de todos os quadros
    for board in data.get("boards", {}).values():
        for list_data in board.get("lists", {}).values():
            if card_id in list_data.get("cards", {}):
                # Remove o card do dicionário
                del list_data["cards"][card_id]
                
                # Remove o card da ordem
                cards_order = list_data.get("cards_order", [])
                if card_id in cards_order:
                    cards_order.remove(card_id)
                
                save_boards(data)
                return jsonify({"success": True, "message": "Card excluído com sucesso"})
    
    return jsonify({"error": "Card não encontrado"}), 404


@app.route('/api/cards/search', methods=['GET'])
def search_cards():
    """Busca cards por texto"""
    query = request.args.get('query', '').lower()
    board_id = request.args.get('board_id')
    
    if not query:
        return jsonify({"error": "Parâmetro de busca 'query' é obrigatório"}), 400
    
    data = load_boards()
    results = []
    
    # Filtra os quadros a serem pesquisados
    boards_to_search = {}
    if board_id:
        if board_id in data.get("boards", {}):
            boards_to_search[board_id] = data["boards"][board_id]
        else:
            return jsonify({"error": "Quadro não encontrado"}), 404
    else:
        boards_to_search = data.get("boards", {})
    
    # Busca os cards
    for b_id, board in boards_to_search.items():
        for l_id, list_data in board.get("lists", {}).items():
            for c_id, card in list_data.get("cards", {}).items():
                # Verifica se o texto aparece no nome ou descrição do card
                if (query in card.get("name", "").lower() or 
                    query in card.get("description", "").lower()):
                    results.append({
                        "id": c_id,
                        "name": card.get("name", ""),
                        "description": card.get("description", ""),
                        "due_date": card.get("due_date", ""),
                        "list_id": l_id,
                        "board_id": b_id,
                        "created_at": card.get("created_at", ""),
                        "archived": card.get("archived", False)
                    })
    
    return jsonify({"cards": results})


# Função para iniciar o servidor
def run_server(host='0.0.0.0', port=5000, debug=False):
    """Inicia o servidor TESS MCP"""
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    # Obtém configurações do ambiente
    host = os.environ.get('TESS_HOST', '0.0.0.0')
    port = int(os.environ.get('TESS_PORT', 5000))
    debug = os.environ.get('TESS_DEBUG', 'False').lower() == 'true'
    
    # Inicia o servidor
    run_server(host=host, port=port, debug=debug) 