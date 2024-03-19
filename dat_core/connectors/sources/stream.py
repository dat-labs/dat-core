import time
from typing import Dict, List, Optional, Iterable, Mapping, Any, Generator
from abc import ABC, abstractmethod
from dat_core.pydantic_models.connector_specification import ConnectorSpecification
from dat_core.pydantic_models.dat_document_stream import DatDocumentStream, SyncMode
from dat_core.pydantic_models.dat_catalog import DatCatalog
from dat_core.pydantic_models.dat_message import DatMessage, DatDocumentMessage, Data, Type, DatStateMessage, StreamState
from dat_core.pydantic_models.stream_metadata import StreamMetadata

def to_snake_case(_str):
    """
    Given a camel_case string, convert it
    to snake case.
    E.g
    ThisIsCamel ---> this_is_camel
    thisIsCamel ---> this_is_camel
    """
    import re
    a = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
    return a.sub(r'_\1', _str).lower()

class Stream(ABC):
    """
    Base abstract class for a Dat Stream
    """
    _state_checkpoint_interval = None

    @classmethod
    @property
    def name(cls) -> str:
        """
        Returns the name of the stream. Ideally it should be a
        camel case string matching the class name.
        """
        # TODO: Make a function for camel case
        return to_snake_case(cls.__name__)

    @property
    def sync_mode(self) -> SyncMode:
        # TODO: Fix return
        return SyncMode.incremental
    
    @property
    def json_schema(self) -> Mapping[str, Any]:
        return self._schema
    
    def get_schema_json(self) -> Dict:
        """
        Get the schema by either reading from the catalog.yml or some
        custom implementation

        Returns:
            Dict: schema of the stream response
        """
        # Default behavior. Otherwise one could have custom implementation
        return self.json_schema
    
    def as_pydantic_model(self) -> DatDocumentStream:
        return DatDocumentStream(
            name=self.name,
            sync_mode=self.sync_mode
        )
    
    def as_record_message(self, doc_chunk: str, data_entity: str, configured_stream: DatDocumentStream) -> DatMessage:
        doc_msg = DatDocumentMessage(
                stream=self.as_pydantic_model(),
                data=Data(
                    document_chunk=doc_chunk,
                    metadata=self.get_metadata(
                        specs=self._config,
                        document_chunk=doc_chunk,
                        data_entity=data_entity
                    )
                ),
                emitted_at=int(time.time()),
                namespace=configured_stream.namespace
            )
        return DatMessage(
            type=Type.RECORD,
            record=doc_msg
        )
    
    def get_metadata(self, specs: ConnectorSpecification, document_chunk: str, data_entity: str) -> StreamMetadata:
        """
        Get necessary metadata to be published which will give a
        hint about the nature of data that is being published

        Args:
            specs (ConnectorSpecification): Connection specification 
            document_chunk (str): A single chunk of text document
            data_entity (str): Data entity represents the source of the document chunk. It
                can be a file_url, some database table, local filepath etc

        Returns:
            StreamMetadata: Object of this class
        """
        metadata = StreamMetadata(
            dat_source=specs.name,
            dat_stream=self.name,
            dat_document_entity=data_entity,
            dat_last_modified=int(time.time()),
            dat_document_chunk=document_chunk
        )
        return metadata
    
    @abstractmethod
    def read_records(self,
        catalog: DatCatalog,
        configured_stream: DatDocumentStream,
        stream_state: StreamState = None
    ) -> Generator[DatMessage, Any, Any]:
        pass
    
    def _should_checkpoint_state(self, cursor_field: str, stream_state: StreamState, record: DatMessage, _record_count: int) -> bool:
        if self._state_checkpoint_interval and _record_count >= self._state_checkpoint_interval:
            return True
        elif stream_state.data and self._compare_cursor_values(
            old_cursor_value=stream_state.data.get(cursor_field),
            current_cursor_value=self._get_cursor_value_from_record(cursor_field, record)
        ):
            return True
        else:
            return False
    
    def _compare_cursor_values(self, old_cursor_value: Any, current_cursor_value: Any) -> bool:
        # Should be implemented by streams
        return False
    
    def _get_cursor_value_from_record(self, cursor_field: str | None, record: DatMessage) -> Any:
        if not cursor_field:
            return None
        
        if record.record.data:
            cursor_value = self._cursor_value_from_record_data(cursor_field, record.record.data)\
                or self._get_cursor_value_from_metadata(cursor_field, record.record.data.metadata)
            return cursor_value
    
    def _cursor_value_from_record_data(self, cursor_field: str, record_data: Data) -> Any:
        return getattr(record_data, cursor_field, None)
    
    def _get_cursor_value_from_metadata(self, cursor_field: str, metadata: StreamMetadata) -> Any:
        return getattr(metadata, cursor_field, None)
    
    def _checkpoint_stream_state(self, configured_stream: DatDocumentStream ,stream_state: Mapping[Any, Any], state_manager: Any) -> DatMessage:
        state_manager.save_stream_state(stream=configured_stream, stream_state=stream_state)
        state_msg = DatStateMessage(
            stream=self.as_pydantic_model(),
            stream_state=stream_state
        )
        return DatMessage(type=Type.STATE, state=state_msg)