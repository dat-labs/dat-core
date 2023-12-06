import os
from abc import abstractmethod
from typing import (Any, Dict, Iterable, Iterator, List,
    Mapping, MutableMapping, Optional, Tuple, Union)
import yaml
from utils import schema_validate
from pydantic_models.dat_message import DatMessage
from pydantic_models.dat_catalog import DatCatalog
from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_catalog import DatCatalog
from connectors.base import ConnectorBase
from connectors.sources.stream import Stream

class SourceBase(ConnectorBase):
    """
    Base abstract Class for all sources
    """
    def discover(self, config: ConnectorSpecification) -> DatCatalog:
        """
        Should publish a connectors capabilities i.e it's catalog

        Args:
            config (ConnectorSpecification): The user-provided configuration as specified by
              the source's spec.

        Returns:
            DatCatalog: Supported streams in the connector
        """
        streams = [stream.as_pydantic_model() for stream in self.streams(config=config)]
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
        for configured_stream in catalog.streams:
            yield from configured_stream.read_records(
                config=config,
                sync_mode=configured_stream.sync_mode,
                cursor_field=None, # TODO: To be implemented,
                stream_state=state,
            )

    @abstractmethod
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Will return the supported streams

        Args:
            config (Mapping[str, Any]): User provided connector specs

        Returns:
            List[Dict]: #TODO return Stream object
        """
        pass
