from abc import abstractmethod
from typing import (
    Any, Dict, List,
    Mapping, Optional, Generator
)
from datetime import datetime
import yaml
import jsonref
from dat_core.pydantic_models import (
    DatMessage,
    StreamState,
    StreamStatus,
    DatCatalog,
    ConnectorSpecification,
    DatDocumentStream,
    ReadSyncMode,
    DatLogMessage,
    Level,
    Type,
    DatStateMessage,
)
from dat_core.connectors.base import ConnectorBase
from dat_core.connectors.sources.stream import Stream

class SourceBase(ConnectorBase):
    """
    Base abstract Class for all sources
    """
    _catalog_class = DatCatalog

    def read_catalog_file(self) -> Dict:
        """
        Read the catalog file and return the json contents
        """
        with open(self._catalog_file) as _c:
            return yaml.safe_load(_c)
        
    def discover(self, config: ConnectorSpecification) -> Dict:
        """
        Should publish a connectors capabilities i.e it's catalog

        Args:
            config (ConnectorSpecification): The user-provided configuration as specified by
              the source's spec.

        Returns:
            DatCatalog: Supported streams in the connector
        """
        _catalog = self._catalog_class.model_json_schema()
        _resolved_catalog =  jsonref.loads(jsonref.dumps(_catalog))
        _document_streams = _resolved_catalog['properties']['document_streams']['items']
        if 'anyOf' in _document_streams:
            _resolved_catalog['properties']['document_streams']['items'] = _document_streams['anyOf'].copy()
            del _document_streams['anyOf']
        else:
            _resolved_catalog['properties']['document_streams']['items'] = [_document_streams.copy()]

        for doc_stream in _resolved_catalog['properties']['document_streams']['items']:
            doc_stream['properties']['advanced']['properties']['splitter_settings']['oneOf'] = doc_stream['properties']['advanced']['properties']['splitter_settings']['anyOf'].copy()
        
        for doc_stream in _resolved_catalog['properties']['document_streams']['items']:
            if 'anyOf' in doc_stream['properties']['advanced']['properties']['splitter_settings']:
                del doc_stream['properties']['advanced']['properties']['splitter_settings']['anyOf']
        return _resolved_catalog
    
    @abstractmethod
    def streams(self, config: Mapping[str, Any], json_schemas: Mapping[str, Mapping[str, Any]]=None) -> List[Stream]:
        """
        Will return the supported streams

        Args:
            config (Mapping[str, Any]): User provided connector specs
            json_schemas (Mapping[str, Mapping[str, Any]]): List of json schemas with each item a dictionary
                with it's key as stream name

        Returns:
            List[Dict]: #TODO return Stream object
        """
        pass

    def read(
        self,
        config: ConnectorSpecification,
        catalog: DatCatalog,
        state: Optional[Mapping[str, StreamState]] = None,
    ) -> Generator[DatMessage, Any, Any]:
        """
        Reads data from a data stream based on the provided configuration and catalog.

        Parameters:
            config (ConnectorSpecification): The configuration object specifying the connector details.
            catalog (DatCatalog): The catalog containing information about the data streams.
            state (Optional[Mapping[str, StreamState]], optional): A mapping of stream names to their current state. Defaults to None.

        Yields:
            Generator[DatMessage, Any, Any]: A generator yielding DatMessage objects containing the read data.

        Raises:
            Exception: If an error occurs during the reading process.

        Returns:
            Generator[DatMessage, Any, Any]: A generator yielding DatMessage objects with the read data.
        """
        stream_instances = {s.name: s for s in self.streams(config)}
        for configured_stream in catalog.document_streams:
            stream_state_data = {}
            yield DatMessage(
                type=Type.STATE,
                state=DatStateMessage(
                    stream=configured_stream,
                    stream_state=StreamState(
                        data=stream_state_data,
                        stream_status=StreamStatus.STARTED,
                    ),
                )
            )
            stream_instance = stream_instances.get(configured_stream.name)
            stream_state = state.get(configured_stream.namespace, StreamState(data={})) if state else StreamState(data={})
            if configured_stream.read_sync_mode == ReadSyncMode.INCREMENTAL:
                configured_stream.cursor_field = configured_stream.cursor_field or stream_instance._default_cursor
                records = self._read_incremental(stream_instance, catalog, configured_stream, stream_state)
            else:
                records = self._read_full_refresh(stream_instance, catalog, configured_stream)

            try:
                first_record = next(records)
                stream_state = self._build_stream_state_from_record(stream_instance, configured_stream, first_record) 
                
                yield stream_instance._checkpoint_stream_state(configured_stream, stream_state)
                yield first_record

                _record_count = 1
                for record in records:
                    _record_count += 1
                    if configured_stream.read_sync_mode == ReadSyncMode.INCREMENTAL and \
                        stream_instance._should_checkpoint_state(
                            configured_stream.cursor_field, stream_state, record, _record_count):
                        stream_state_data = {
                            configured_stream.cursor_field: stream_instance._get_cursor_value_from_record(
                                configured_stream.cursor_field, record)
                        }
                        stream_state = StreamState(
                            data=stream_state_data,
                            stream_status=StreamStatus.RUNNING,
                        )
                        yield stream_instance._checkpoint_stream_state(configured_stream, stream_state)
                    yield record
                yield DatMessage(
                    type=Type.STATE,
                    state=DatStateMessage(
                        stream=configured_stream,
                        stream_state=StreamState(
                            data=stream_state_data,
                            stream_status=StreamStatus.COMPLETED,
                        ),
                    )
                )
            except StopIteration:
                _log_msg = DatMessage(
                    type=Type.LOG,
                    log=DatLogMessage(
                        level=Level.WARN,
                        message='The source didnt return any data'
                    )
                )
                print(_log_msg.model_dump_json(), flush=True)

    def _build_stream_state_from_record(self,
        stream_instance: Stream,
        configured_stream: DatDocumentStream,
        record: DatMessage
    ) -> StreamState:
        stream_state_data = {}
        if configured_stream.cursor_field:
            stream_state_data[configured_stream.cursor_field] = stream_instance._get_cursor_value_from_record(
                configured_stream.cursor_field, record)
        stream_state = StreamState(
            data=stream_state_data,
            stream_status=StreamStatus.RUNNING,
        )
        return stream_state

    def _read_incremental(self,
        stream_instance: Stream,
        catalog: DatCatalog,
        configured_stream: DatDocumentStream,
        stream_state: StreamState
    ) -> Generator[DatMessage, Any, Any]:
        """
        If stream_state is available, pass the cursor value so that data can
        be fetched incrementally
        """
        _cursor_value = stream_state.data.get(configured_stream.cursor_field)
        yield from stream_instance.read_records(
                catalog=catalog,
                configured_stream=configured_stream,
                cursor_value=_cursor_value
            )
    
    def _read_full_refresh(self,
        stream_instance: Stream,
        catalog: DatCatalog,
        configured_stream: DatDocumentStream,
    ) -> Generator[DatMessage, Any, Any]:
        """
        Fetch the entire data
        """
        yield from stream_instance.read_records(
                catalog=catalog,
                configured_stream=configured_stream,
                cursor_value=None
            )
