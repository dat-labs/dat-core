import itertools
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Generator, Iterable, List, Optional, Tuple, TypeVar, Dict
from pydantic_models.dat_message import DatMessage, Type, DatDocumentMessage, Data



class Seeder(ABC):

    def __init__(self, config: Any):
        self.config = config

    @abstractmethod
    def seed(self, document_chunks: List[DatDocumentMessage], namespace: str, stream: str) -> None:
        """
        This method should be used to index documents in the destination.
        """
        pass

    @abstractmethod
    def delete(self, filter: Dict[Any, str], namespace: str) -> None:
        """
        This method should be used to delete documents in the destination.
        """
        pass

    @abstractmethod
    def check(self) -> Optional[str]:
        """
        This method should be used to check the connection to the destination.
        """
        pass
