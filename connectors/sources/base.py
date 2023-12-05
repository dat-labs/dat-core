import os
from abc import abstractmethod
from typing import (Any, Dict, Iterable, Iterator, List,
    Mapping, MutableMapping, Optional, Tuple, Union)
import yaml
from utils import schema_validate
from pydantic_models.dat_message import DatMessage
from pydantic_models.dat_catalog import DatCatalog
from pydantic_models.connector_specification import ConnectorSpecification
from connectors.base import ConnectorBase

class SourceBase(ConnectorBase):
    """
    Base abstract Class for all sources
    """

    def __init__(self) -> None:
        super().__init__()

    def discover(self, config: Mapping[str, Any]) -> DatCatalog:
        """
        Should publish a connectors capabilities i.e it's catalog

        Args:
            config (Mapping[str, Any]): The user-provided configuration as specified by
              the source's spec.

        Returns:
            DatCatalog: Supported streams in the connector
        """
        streams = [stream for stream in self.streams(config=config)]
        return DatCatalog(streams=streams)

    def read(
        self,
        config: Mapping[str, Any],
        catalog: Mapping[str, Any],
        state: Optional[Union[List[Dict], MutableMapping[str, Any]]] = None,
    ) -> Iterator[DatMessage]:
        """
        The read operation which will read from the source based on the configured streams

        Args:
            config (Mapping[str, Any]): The user-provided configuration as specified by
              the source's spec.
            catalog (Mapping[str, Any]): User provided configured catalog
            state (Optional[Union[List[Dict], MutableMapping[str, Any]]], optional): If the
              source supports state maintenance. Defaults to None.

        Yields:
            Iterator[Dict]: Each row should be wrapped around a DatMessage obj
        """
        pass

    @abstractmethod
    def streams(self, config: Mapping[str, Any]) -> List[Dict]:
        """
        Will return the supported streams

        Args:
            config (Mapping[str, Any]): User provided connector specs

        Returns:
            List[Dict]: #TODO return Stream object
        """
        pass
