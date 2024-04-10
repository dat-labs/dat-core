from collections import defaultdict
from abc import ABC
from typing import Any, Dict, Iterable, List, Optional, Tuple
from dat_core.connectors.destinations.vector_db_helpers.seeder import Seeder
from dat_core.pydantic_models import (
    DatMessage, Type, DatDocumentMessage,
    StreamStatus, DatCatalog,
    StreamMetadata, WriteSyncMode,
    Level, DatLogMessage
)


class DataProcessor(ABC):
    """
    This class is responsible for processing the data and seeding it to the destination.

    Args:
        config: The configuration for the data processor.
        seeder: The seeder object to seed the data to the destination.
        batch_size: The batch size for processing the data.
    """

    def __init__(
        self, config: Any, seeder: Seeder, batch_size: int,
    ) -> None:
        """
        Initialize the DataProcessor object.

        Args:
            config (Any): The configuration object.
            seeder (Seeder): The seeder object.
            batch_size (int): The batch size for processing data.

        Returns:
            None
        """
        self.config = config
        self.seeder = seeder
        self.batch_size = batch_size
        self._init_batch()
        self._init_class_vars()

    def _init_class_vars(self) -> None:
        """
        Initializes the class variables.
        """
        self.number_of_documents_per_stream: Dict[Tuple[str, str], int] = defaultdict(int)

    def _init_batch(self) -> None:
        """
        Initialize batch variables.
        """
        self.documents: Dict[Tuple[str, str]: Dict[str, List[DatDocumentMessage]]] = defaultdict(
            lambda: defaultdict(list[DatDocumentMessage]))
        self.number_of_documents: int = 0

    def _process_batch(self) -> None:
        """
        Process a batch of documents.

        Returns:
            Iterable[DatLogMessage]: An iterable of DatLogMessage objects.

        Yields:
            Iterator[Iterable[DatLogMessage]]: An iterator of iterable DatLogMessage objects.
        """
        for (namespace, stream), documents in self.documents.items():
            for _, chunks in documents.items():
                self.number_of_documents_per_stream[(namespace, stream)] += len(chunks)
                self.seeder.seed(chunks, namespace, stream)
        self._init_batch()

    def _process_delete(self, metadata: StreamMetadata, namespace: str) -> None:
        """
        Process the delete operation for documents with the given metadata and namespace.

        Args:
            metadata (StreamMetadata): The metadata of the documents to be deleted.
            namespace (str): The namespace of the documents.

        Yields:
            DatLogMessage: A log message indicating the deletion operation.

        """
        self.seeder.delete(filter=metadata, namespace=namespace)

    def processor(self, configured_catalog: DatCatalog, input_messages: Iterable[DatMessage]) -> Iterable[DatMessage]:
        """
        Process the input messages and perform data processing.

        Args:
            configured_catalog (DatCatalog): The configured catalog.
            input_messages (Iterable[DatMessage]): The input messages to process.

        Yields:
            DatMessage: The processed messages.

        Raises:
            ValueError: If the stream specified in the message is not found in the configured catalog.
        """
        yield DatMessage(type=Type.LOG, log=DatLogMessage(level=Level.INFO, message="Initializing data processor."))
        yield DatMessage(type=Type.LOG, log=DatLogMessage(level=Level.INFO, message=f"Processing {len(input_messages)} messages."))
        self.seeder.initiate_sync(configured_catalog)
        for message in input_messages:
            if message.type == Type.STATE:
                if message.state.stream_state.stream_status == StreamStatus.STARTED:
                    if message.state.stream.name not in [stream.name for stream in configured_catalog.document_streams]:
                        raise ValueError(f"Stream {message.state.stream.name} not found in configured catalog.")
                    idx = self._find_stream_idx(message.state.stream.name, configured_catalog)
                    if configured_catalog.document_streams[idx].write_sync_mode == WriteSyncMode.UPSERT:
                        self._process_delete(message.record.data.metadata, message.record.namespace)
                    yield message
                else:
                    self._process_batch()
                    yield DatMessage(
                        type=Type.LOG,
                        log=DatLogMessage(level=Level.INFO, message=f"Processed {self.number_of_documents_per_stream} documents.")
                    )
                    yield message
            if message.type == Type.RECORD:
                self.number_of_documents += 1
                self.documents[
                    (message.record.namespace, message.record.stream.name)][
                        message.record.data.metadata.dat_document_entity].append(
                            message.record)
                if self.number_of_documents >= self.batch_size:
                    self._process_batch()
                    yield DatMessage(
                        type=Type.LOG,
                        log=DatLogMessage(level=Level.INFO, message=f"Processed {self.number_of_documents_per_stream} documents.")
                    )
        self._process_batch()
        yield DatMessage(
            type=Type.LOG,
            log=DatLogMessage(level=Level.INFO, message=f"Processed {self.number_of_documents_per_stream} documents.")
        )

    def _find_stream_idx(self, stream_name: str, catalog: DatCatalog) -> Optional[int]:
        """
        Finds the index of a stream with the given name in the catalog.

        Args:
            stream_name (str): The name of the stream to find.
            catalog (DatCatalog): The catalog containing the streams.

        Returns:
            Optional[int]: The index of the stream if found, None otherwise.
        """
        for idx, stream in enumerate(catalog.document_streams):
            if stream.name == stream_name:
                return idx
        return None
