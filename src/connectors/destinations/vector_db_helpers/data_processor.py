from collections import defaultdict
from dataclasses import dataclass
from abc import ABC
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, TypeVar
from connectors.destinations.vector_db_helpers.seeder import Seeder
from pydantic_models.dat_message import DatMessage, Type, DatDocumentMessage, Data, StreamStatus
from pydantic_models.dat_catalog import DatCatalog
from pydantic_models.stream_metadata import StreamMetadata


class DataProcessor(ABC):
    """
    Base abstract class for a Data Processor.
    """

    def __init__(
        self, config: Any, seeder: Seeder, batch_size: int,
    ) -> None:
        self.config = config
        self.seeder = seeder
        self.batch_size = batch_size
        self._init_batch()
        self._init_class_vars()
    
    def _init_class_vars(self) -> None:
        self.number_of_documents: int = 0
        self.metadata_filter: Dict[str, Any] = {}

    def _init_batch(self) -> None:
        self.document_chunks: List = []
        self.documents: Dict[Tuple[str, str]: Dict[str, List]] = defaultdict(lambda: defaultdict(list))
        self.document_deleted_cnt: Dict[Tuple[str, str]: Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def _process_batch(self) -> None:
        # if len(self.document_chunks) > 0:
        #     self.seeder.seed(self.document_chunks, self.document_chunks[0].record.namespace, self.document_chunks[0].record.stream)
        #     print(f"Processed {self.number_of_documents} documents.")
        for (namespace, stream), documents in self.documents.items():
            for document_entity, chunks in documents.items():
                self.seeder.seed(chunks, namespace, stream)
        print(f"Processed {self.number_of_documents} documents.")
        self._init_batch()

    def _process_delete(self, metadata: StreamMetadata, namespace: str) -> None:
        print(f"Deleting documents with metadata: {metadata}")
        self.seeder.delete(filter=metadata, namespace=namespace)

    def processor(self, configured_catalog: DatCatalog, input_messages: Iterable[DatMessage]) -> Iterable[DatMessage]:
        print(f"Processing {len(input_messages)} messages.")
        for message in input_messages:
            # print(f"Processing message: {message}")
            if message.type == Type.STATE:
                if message.state.stream_state.stream_status == StreamStatus.STARTED:
                    if "upsert":
                        # self._prepare_metadata_filter(message.record.data.metadata)
                        self._process_delete(message.record.data.metadata, message.record.namespace)
                    yield message
                else:
                    self._process_batch()
                    yield message
            if message.type == Type.RECORD:
                self.number_of_documents += 1
                self.documents[
                    (message.record.namespace, message.record.stream.name)][
                        message.record.data.metadata.dat_document_entity].append(
                            message.record)
                if self.number_of_documents >= self.batch_size:
                    self._process_batch()
        self._process_batch()

    # def _prepare_metadata_filter(self, metadata: StreamMetadata) -> None:
    #     self.metadata_filter = self.seeder.metadata_filter(metadata)
    #     print(f"Metadata filter: {self.metadata_filter}")
