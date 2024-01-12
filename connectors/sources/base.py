import os
from abc import abstractmethod
from typing import (Any, Dict, Iterable, Iterator, List,
    Mapping, MutableMapping, Optional, Tuple, Union)
import yaml
from utils import schema_validate
from pydantic_models.dat_message import (
    DatMessage,
    DatStateMessage,
    Stream as StateMessageStream,
    StreamDescriptor,
    StreamState,
    StreamStatus,
    Type,
    DatDocumentMessage
)

from pydantic_models.dat_catalog import DatCatalog
from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_catalog import DatCatalog
from connectors.base import ConnectorBase
from connectors.sources.stream import Stream

class SourceBase(ConnectorBase):
    """
    Base abstract Class for all sources
    """
    def read_catalog_file(self) -> Dict:
        """
        Read the catalog file and return the json contents
        """
        with open(self._catalog_file, 'r') as _f:
            catalog_json = yaml.safe_load(_f)
            return catalog_json
        
    def discover(self, config: ConnectorSpecification) -> DatCatalog:
        """
        Should publish a connectors capabilities i.e it's catalog

        Args:
            config (ConnectorSpecification): The user-provided configuration as specified by
              the source's spec.

        Returns:
            DatCatalog: Supported streams in the connector
        """
        catalog_json = self.read_catalog_file()
        streams = catalog_json['properties']['streams']['items']
        json_schemas = {_s['properties']['name']: _s['properties']['json_schema']['properties'] for _s in streams}
        streams = [stream.as_pydantic_model() for stream in self.streams(config=config, json_schemas=json_schemas)]
        return DatCatalog(document_streams=streams)

    def read(
        self,
        config: ConnectorSpecification,
        catalog: DatCatalog,
        state: Optional[Union[List[Dict], MutableMapping[str, Any]]] = None,
    ) -> Iterator[DatMessage]:
        """
        The read operation which will read from the source based on the configured streams

        Args:
            config (ConnectorSpecification): The user-provided configuration as specified by
              the source's spec.
            catalog (DatCatalog): User provided configured catalog
            state (Optional[Union[List[Dict], MutableMapping[str, Any]]], optional): If the
              source supports state maintenance. Defaults to None.

        Yields:
            Iterator[Dict]: Each row should be wrapped around a DatMessage obj
        """
        stream_instances = {s.name: s for s in self.streams(config)}
        for configured_stream in catalog.document_streams:
            stream_instance = stream_instances.get(configured_stream.name)
            records = stream_instance.read_records(
                config=config,
                sync_mode=configured_stream.sync_mode,
                cursor_field=None, # TODO: To be implemented,
                stream_state=state,
            )
            try:
                first_record = next(records)
                start_msg = DatMessage(
                    type=Type.STATE,
                    state=DatStateMessage(
                        stream=StateMessageStream(
                            stream_descriptor=StreamDescriptor(name=configured_stream.name),
                            stream_state=StreamState(
                                data={},
                                stream_status=StreamStatus.STARTED
                            )
                        )
                    ),
                    record=first_record.record
                )
                yield start_msg
                yield first_record
                for record in records:
                    yield record
            except Exception as exc:
                # TODO: Add specific exception
                raise


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
