from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict
from dat_core.pydantic_models import (
    StreamMetadata, DatDocumentMessage,
    DatCatalog,
)


class Loader(ABC):
    """
    Abstract base class for loaders that interact with a destination.

    Attributes:
        METADATA_FILTER_FIELDS (List[str]): List of metadata filter fields.
        METADATA_DAT_STREAM_FIELD (str): Metadata field for dat stream.

    Args:
        config (Any): Configuration for the loader.
    """

    METADATA_FILTER_FIELDS = ["dat_source", "dat_stream", "dat_document_entity"]
    METADATA_DAT_STREAM_FIELD = "dat_stream"

    def __init__(self, config: Any):
        self.config = config

    @abstractmethod
    def load(self, document_chunks: List[DatDocumentMessage], namespace: str, stream: str) -> None:
        """
        Abstract method to load documents in the destination.

        Args:
            document_chunks (List[DatDocumentMessage]): List of document chunks to load.
            namespace (str): Namespace of the documents.
            stream (str): Stream of the documents.

        Returns:
            None
        """
        pass

    @abstractmethod
    def delete(self, filter: Dict[Any, str], namespace: str) -> None:
        """
        Abstract method to delete documents in the destination.

        Args:
            filter (Dict[Any, str]): Filter to specify which documents to delete.
            namespace (str): Namespace of the documents.

        Returns:
            None
        """
        pass

    @abstractmethod
    def check(self) -> Optional[str]:
        """
        Abstract method to check the connection to the destination.

        Returns:
            Optional[str]: Error message if the connection check fails, None otherwise.
        """
        pass

    def initiate_sync(self, configured_catalog: DatCatalog) -> None:
        """
        Initiates the synchronization process with the specified configured catalog.

        Args:
            configured_catalog (DatCatalog): The configured catalog to synchronize with.

        Returns:
            None
        """
        pass

    @abstractmethod
    def metadata_filter(self, metadata: StreamMetadata) -> Any:
        """
        Abstract method to filter documents by metadata.

        Args:
            metadata (StreamMetadata): Metadata of the document.

        Returns:
            Any: Filtered value based on the metadata.
        """
        pass
