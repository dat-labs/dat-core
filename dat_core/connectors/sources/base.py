import urllib.request
from abc import abstractmethod
from typing import (Any, Dict, Iterable, Iterator, List,
    Mapping, MutableMapping, Optional, Tuple, Union)
import yaml
from dat_core.pydantic_models.dat_message import (
    DatMessage,
    DatStateMessage,
    StreamState,
    StreamStatus,
    Type,
)

from dat_core.pydantic_models.dat_catalog import DatCatalog
from dat_core.pydantic_models.connector_specification import ConnectorSpecification
from dat_core.pydantic_models.dat_catalog import DatCatalog
from dat_core.pydantic_models.configured_dat_catalog import ConfiguredDatCatalog
from dat_core.connectors.base import ConnectorBase
from dat_core.connectors.sources.stream import Stream

class SourceBase(ConnectorBase):
    """
    Base abstract Class for all sources
    """
    def read_catalog_file(self) -> Dict:
        """
        Read the catalog file and return the json contents
        """
        with urllib.request.urlopen(self._catalog_file) as response:
            return yaml.safe_load(response.read().decode())
        
    def discover(self, config: ConnectorSpecification) -> Dict:
        """
        Should publish a connectors capabilities i.e it's catalog

        Args:
            config (ConnectorSpecification): The user-provided configuration as specified by
              the source's spec.

        Returns:
            DatCatalog: Supported streams in the connector
        """
        catalog_json = self.read_catalog_file()
        if catalog_json:
            return catalog_json
        else:
            # TODO: Write logic to return available streams
            return {}

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
                catalog=catalog,
                configured_stream=configured_stream,
                stream_state=state
            )
            try:
                first_record = next(records)
                start_msg = DatMessage(
                    type=Type.STATE,
                    state=DatStateMessage(
                        stream=configured_stream,
                        stream_state=StreamState(
                            data={},
                            stream_status=StreamStatus.STARTED
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
