from collections import defaultdict
from dataclasses import dataclass
from abc import ABC, abstractmethod, abstractclassmethod
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, TypeVar
from connectors.destinations.vector_db_helpers.seeder import Seeder
from pydantic_models.dat_message import DatMessage, Type, DatDocumentMessage, Data
from pydantic_models.dat_catalog import DatCatalog

@dataclass
class Chunk:
    page_content: Optional[str]
    metadata: Dict[str, Any]
    record: DatDocumentMessage
    embedding: Optional[List[float]] = None

METADATA_FILTER_FIELDS = ["dat_source", "dat_stream", "dat_document_entity"]


class DataProcessor(ABC):
    """
    Base abstract class for a Data Processor.
    """

    def __init__(
        self, config: Any, seeder: Seeder, batch_size: int, omit_raw_text: bool
    ) -> None:
        self.config = config
        self.seeder = seeder
        self.batch_size = batch_size
        self.omit_raw_text = omit_raw_text
        self._init_batch()
        self._init_class_vars()
    
    def _init_class_vars(self) -> None:
        self.number_of_documents = 0
        self.metadata_filter = {}

    def _init_batch(self) -> None:
        self.document_chunks: List[Chunk] = []

    def _process_batch(self) -> None:
        print(f"Documents: {self.document_chunks}")
        if len(self.document_chunks) > 0:
            self.seeder.seed(self.document_chunks, self.document_chunks[0].record.namespace, self.document_chunks[0].record.stream)
            print(f"Processed {self.number_of_documents} documents.")

        self._init_batch()

    def _process_delete(self, metadata: Mapping[str, Any], namespace: str) -> None:
        print(f"Deleting documents with metadata: {metadata}")
        self.seeder.delete(filter=metadata, namespace=namespace)

    def processor(self, configured_catalog: DatCatalog, input_messages: Iterable[DatMessage]) -> Iterable[DatMessage]:
        for message in input_messages:
            if message.type == Type.RECORD:
                print(f"message: {message}")
                self.number_of_documents += 1
                if self.number_of_documents == 1:
                    self._prepare_metadata_filter(message.record.data.metadata)
                    self._process_delete(self.metadata_filter, message.record.namespace)
                self.document_chunks.append(
                    Chunk(
                        page_content=message.record.data.document_chunk,
                        metadata=message.record.data.metadata,
                        record=message.record,
                        embedding=message.record.data.vectors,
                    )
                )
                if len(self.document_chunks) >= self.batch_size:
                    self._process_batch()
        self._process_batch()

    def _prepare_metadata_filter(self, metadata: Dict[str, Any]) -> None:
        for key, value in metadata.items():
            if key in METADATA_FILTER_FIELDS:
                self.metadata_filter[key] = {"$eq": value}
