from collections import defaultdict
from abc import ABC
from typing import Any, Dict, Iterable, List, Optional, Tuple
from dat_core.connectors.destinations.vector_db_helpers.seeder import Seeder
from dat_core.pydantic_models import (
    DatMessage, Type, DatDocumentMessage,
    StreamStatus, DatCatalog,
    StreamMetadata, WriteSyncMode
)


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
        self.metadata_filter: Dict[str, Any] = {}

    def _init_batch(self) -> None:
        self.number_of_documents: int = 0
        self.documents: Dict[Tuple[str, str]: Dict[str, List[DatDocumentMessage]]] = defaultdict(
            lambda: defaultdict(list[DatDocumentMessage]))
        # self.document_deleted_cnt: Dict[Tuple[str, str]: Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def _process_batch(self) -> None:
        # if len(self.document_chunks) > 0:
        #     self.seeder.seed(self.document_chunks, self.document_chunks[0].record.namespace, self.document_chunks[0].record.stream)
        #     print(f"Processed {self.number_of_documents} documents.")
        for (namespace, stream), documents in self.documents.items():
            for _, chunks in documents.items():
                self.seeder.seed(chunks, namespace, stream)
        print(f"Processed {self.number_of_documents} documents.")
        self._init_batch()

    def _process_delete(self, metadata: StreamMetadata, namespace: str) -> None:
        print(f"Deleting documents with metadata: {metadata}")
        self.seeder.delete(filter=metadata, namespace=namespace)

    def processor(self, configured_catalog: DatCatalog, input_messages: Iterable[DatMessage]) -> Iterable[DatMessage]:
        print(f"Processing {len(input_messages)} messages.")
        self.pre_processor(configured_catalog)
        for message in input_messages:
            if message.type == Type.STATE:
                if message.state.stream_state.stream_status == StreamStatus.STARTED:
                    if message.state.stream.name not in [stream.name for stream in configured_catalog.document_streams]:
                        raise ValueError(f"Stream {message.state.stream.name} not found in configured catalog.")
                    idx = self._find_stream_idx(message.state.stream.name, configured_catalog)
                    if configured_catalog.document_streams[idx].write_sync_mode == WriteSyncMode.UPSERT:
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

    def pre_processor(self, config: DatCatalog) -> None:
        for stream in config.document_streams:
            if stream.write_sync_mode == WriteSyncMode.REPLACE:
                self.seeder.dest_sync(stream.namespace)

    def _find_stream_idx(self, stream_name: str, catalog: DatCatalog) -> Optional[int]:
        for idx, stream in enumerate(catalog.document_streams):
            if stream.stream.name == stream_name:
                return idx
        return None

    # def _prepare_metadata_filter(self, metadata: StreamMetadata) -> None:
    #     self.metadata_filter = self.seeder.metadata_filter(metadata)
    #     print(f"Metadata filter: {self.metadata_filter}")
