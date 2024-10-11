import json
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Tuple
from dat_core.connectors.destinations.loader import Loader
from dat_core.pydantic_models import (
    DatMessage, Type, DatDocumentMessage,
    StreamStatus, DatCatalog, WriteSyncMode,
    Level, DatLogMessage
)
from dat_core.loggers import logger


class DataProcessor:
    """
    This class is responsible for processing the data and loading it to the destination.

    Args:
        config: The configuration for the data processor.
        loader: The loader object to load the data to the destination.
        batch_size: The batch size for processing the data.
    """

    def __init__(
        self, config: Any, loader: Loader, batch_size: int,
    ) -> None:
        """
        Initialize the DataProcessor object.

        Args:
            config (Any): The configuration object.
            loader (Loader): The loader object.
            batch_size (int): The batch size for processing data.

        Returns:
            None
        """
        self.config = config
        self.loader = loader
        self.batch_size = batch_size
        self._init_class_vars()

    def _init_class_vars(self) -> None:
        """
        Initializes the class variables.
        """
        self.n_records_per_stream: Dict[Tuple[str, str], int] = defaultdict(int)
        self.stream_write_sync_modes: Dict[Tuple[str, str], WriteSyncMode] = {}

    def _initialize_write_sync_modes(self, configured_catalog: DatCatalog) -> None:
        """
        Initializes the write_sync_mode for each stream based on the configured catalog.
        """
        for catalog_entry in configured_catalog.document_streams:
            key = (catalog_entry.namespace, catalog_entry.name)
            self.stream_write_sync_modes[key] = catalog_entry.write_sync_mode

    def _process_batch(self, namespace: str, stream: str, dat_messages: List[DatMessage]) -> None:
        """
        Process a batch of documents and load them to the destination.

        Args:
            namespace (str): The namespace of the stream.
            stream (str): The stream name.
            dat_messages (List[DatMessage]): The list of DatMessage objects in the batch.

        Returns:
            None
        """
        write_sync_mode = self.stream_write_sync_modes.get((namespace, stream))
        if write_sync_mode == WriteSyncMode.UPSERT.name:
            self._process_delete(dat_messages)

        documents = [msg.record for msg in dat_messages]
        self.n_records_per_stream[(namespace, stream)] += len(documents)

        self.loader.load(documents, namespace, stream)
    
    def _process_delete(self, dat_messages) -> None:
        """
        Process the delete operation for documents with the given metadata and namespace.

        Args:
            metadata (StreamMetadata): The metadata of the documents to be deleted.
            namespace (str): The namespace of the documents.

        Yields:
            DatLogMessage: A log message indicating the deletion operation.

        """
        logger.info("Write Sync Mode is set to 'UPSERT'. Processing delete operation.")
        first_record = dat_messages[0].record #Getting first record because all the records in the batch should belong to one stream and namespace
        stream = first_record.stream.name
        namespace = first_record.namespace
        ids = {getattr(msg.record.data.metadata, self.loader.METADATA_DAT_RECORD_ID_FIELD) for msg in dat_messages}
        _filter={
                self.loader.METADATA_DAT_STREAM_FIELD: stream,
                self.loader.METADATA_DAT_RECORD_ID_FIELD: list(ids) + ["not_set"],
                self.loader.METADATA_DAT_RUN_ID_FIELD: first_record.data.metadata.dat_run_id,
                self.loader.METADATA_DAT_SOURCE_FIELD: first_record.data.metadata.dat_source,
            }
        _filter = self.loader.prepare_metadata_filter(_filter)
        logger.info(f"Deleting with filter: {_filter}")
        self.loader.delete(_filter, namespace)

    def processor(self, configured_catalog: DatCatalog, input_messages: Iterable[DatMessage]) -> Iterable[DatMessage]:
        """
        Process the input messages and load data in batches.

        Args:
            configured_catalog (DatCatalog): The configured catalog.
            input_messages (Iterable[DatMessage]): The input messages to process.

        Yields:
            DatMessage: The processed messages.

        Raises:
            ValueError: If the stream specified in the message is not found in the configured catalog.
        """
        documents: Dict[Tuple[str, str], List[DatMessage]] = defaultdict(list)
        total_documents = 0

        def yield_n_docs_per_stream():
            for (namespace, stream_name), n_docs in self.n_records_per_stream.items():
                logger.info(json.dumps({'namespace': namespace, 'stream_name':
                         stream_name, 'n_docs_processed': n_docs, }))

        logger.info("Intializing data processor.")
        logger.info(f"Configured catalog: {configured_catalog.model_dump_json()}")
        logger.debug(f"Processing {len(input_messages)} messages.")

        self._initialize_write_sync_modes(configured_catalog)

        self.loader.initiate_sync(configured_catalog)

        for message in input_messages:
            if message.type == Type.STATE:
                # Directly yield state messages and logs
                yield message
                if message.state.stream_state.stream_status != StreamStatus.STARTED:
                    # yield from yield_n_docs_per_stream(dict(self.n_records_per_stream))
                    yield_n_docs_per_stream()
            elif message.type == Type.RECORD:
                key = (message.record.namespace, message.record.stream.name)
                if key not in self.stream_write_sync_modes:
                    logger.error(f"Stream {key} not found in configured catalog.")
                    raise ValueError(f"Stream {key} not found in configured catalog.")

                # Accumulate records
                documents[key].append(message)
                total_documents += 1

                # Process batch when threshold is reached
                if total_documents >= self.batch_size:
                    for (namespace, stream), dat_messages in documents.items():
                        self._process_batch(namespace, stream, dat_messages)

                    # Reset counters after processing
                    total_documents = 0
                    documents.clear()
                    # yield from yield_n_docs_per_stream(dict(self.n_records_per_stream))
                    yield_n_docs_per_stream()

        # Process any remaining documents after loop
        if documents:
            for (namespace, stream), dat_messages in documents.items():
                self._process_batch(namespace, stream, dat_messages)
            # yield from yield_n_docs_per_stream(dict(self.n_records_per_stream))
            yield_n_docs_per_stream()
