from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union

class TaskManager(ABC):
    """
    Classe base abstrata para gerenciadores de tarefas.
    Define a interface comum para diferentes implementações de gerenciadores.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de tarefas."""
        pass
    
    @abstractmethod
    def listar_agentes(self) -> List[Dict[str, Any]]:
        """Lista todos os agentes disponíveis."""
        raise NotImplementedError("Esta é uma classe abstrata. Implemente este método na subclasse.")
    
    @abstractmethod
    def obter_agente(self, agent_id: str) -> Dict[str, Any]:
        """Obtém detalhes de um agente específico."""
        raise NotImplementedError("Esta é uma classe abstrata. Implemente este método na subclasse.")
    
    @abstractmethod
    def executar_agente(self, agent_id: str, **params) -> Dict[str, Any]:
        """Executa um agente com os parâmetros especificados."""
        raise NotImplementedError("Esta é uma classe abstrata. Implemente este método na subclasse.")
    
    @abstractmethod
    def listar_arquivos(self) -> List[Dict[str, Any]]:
        """Lista todos os arquivos disponíveis."""
        raise NotImplementedError("Esta é uma classe abstrata. Implemente este método na subclasse.")
    
    @abstractmethod
    def vincular_arquivo(self, agent_id: str, file_id: str) -> Dict[str, Any]:
        """Vincula um arquivo a um agente."""
        raise NotImplementedError("Esta é uma classe abstrata. Implemente este método na subclasse.")
    
    @abstractmethod
    def get_boards(self) -> List[Dict[str, Any]]:
        """Retorna todos os quadros disponíveis"""
        raise NotImplementedError("Esta é uma classe abstrata. Implemente este método na subclasse.")
    
    @abstractmethod
    def create_board(self, name: str, description: str = "") -> Dict[str, Any]:
        """Cria um novo quadro"""
        raise NotImplementedError("Esta é uma classe abstrata. Implemente este método na subclasse.")
    
    @abstractmethod
    def delete_board(self, board_id: str) -> Dict[str, Any]:
        """Exclui um quadro"""
        raise NotImplementedError("Esta é uma classe abstrata. Implemente este método na subclasse.")
    
    @abstractmethod
    def get_lists(self, board_id: str) -> List[Dict[str, Any]]:
        """Retorna todas as listas de um quadro"""
        raise NotImplementedError("Esta é uma classe abstrata. Implemente este método na subclasse.")
    
    @abstractmethod
    def create_list(self, board_id: str, name: str) -> Dict[str, Any]:
        """Cria uma nova lista em um quadro"""
        raise NotImplementedError("Esta é uma classe abstrata. Implemente este método na subclasse.")
    
    @abstractmethod
    def get_cards(self, list_id: str) -> List[Dict[str, Any]]:
        """Retorna todos os cards de uma lista"""
        raise NotImplementedError("Esta é uma classe abstrata. Implemente este método na subclasse.")
    
    @abstractmethod
    def create_card(self, list_id: str, name: str, description: str = "", due_date: str = "") -> Dict[str, Any]:
        """Cria um novo card em uma lista"""
        raise NotImplementedError("Esta é uma classe abstrata. Implemente este método na subclasse.")
    
    @abstractmethod
    def archive_card(self, card_id: str) -> Dict[str, Any]:
        """Arquiva um card"""
        raise NotImplementedError("Esta é uma classe abstrata. Implemente este método na subclasse.")
    
    @abstractmethod
    def search_cards(self, query: str, board_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Busca cards por texto"""
        raise NotImplementedError("Esta é uma classe abstrata. Implemente este método na subclasse.") 