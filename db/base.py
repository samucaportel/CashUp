"""
Interface abstrata para conectores de banco de dados.
Permite trocar Oracle/Firebird/SQL Server sem alterar a lógica de sync.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class DatabaseConnector(ABC):
    """Interface base para conectores de banco de dados."""

    @abstractmethod
    def connect(self) -> None:
        """Estabelece conexão com o banco."""
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Fecha conexão com o banco."""
        ...

    @abstractmethod
    def execute_query(self, sql: str, params: dict | None = None) -> list[dict[str, Any]]:
        """
        Executa uma query SELECT e retorna lista de dicts.
        Cada dict representa uma linha com {coluna: valor}.
        """
        ...

    @abstractmethod
    def execute_command(self, sql: str, params: dict | None = None) -> int:
        """
        Executa um INSERT/UPDATE/DELETE e retorna qtd de linhas afetadas.
        """
        ...

    @abstractmethod
    def is_connected(self) -> bool:
        """Verifica se a conexão está ativa."""
        ...

    def load_query(self, query_file: str, queries_dir: Path) -> str:
        """Carrega SQL de um arquivo .sql na pasta queries/."""
        file_path = queries_dir / query_file
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo SQL não encontrado: {file_path}")
        return file_path.read_text(encoding="utf-8")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
