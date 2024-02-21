from abc import ABC, abstractmethod
from typing import Any, Generator, Iterable, List, Optional, Tuple, TypeVar, Dict
from dat_core.pydantic_models.dat_message import DatMessage, Type, DatDocumentMessage, Data
from dat_core.pydantic_models.stream_metadata import StreamMetadata


class Seeder(ABC):

    METADATA_FILTER_FIELDS = ["dat_source", "dat_stream", "dat_document_entity"]

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

    @abstractmethod
    def metadata_filter(self, metadata: StreamMetadata) -> Dict[str, Any]:
        """
        This method should be used to filter documents by metadata.
        """
        pass
