import os
from abc import ABC, abstractmethod
from typing import (Any, Dict, Iterable, Iterator, List,
    Mapping, MutableMapping, Optional, Tuple, Union)
import yaml
from utils import schema_validate
from pydantic_models.dat_message import DatMessage
from pydantic_models.dat_catalog import DatCatalog
from pydantic_models.connector_specification import ConnectorSpecification

class SourceBase(ABC):
    """
    Base abstract Class for all sources
    """
    _spec_file = None

    def __init__(self) -> None:
        super().__init__()
    
    @abstractmethod
    def check_connection(self, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        Based on the given config, it will check if connection to source can be
        established.

        Args:
            config (Mapping[str, Any]): The user-provided configuration as specified by
              the source's spec.

        Returns:
            Tuple[bool, Optional[Any]]: If the bool is True, then connection is established and
            no errors are returned. Otherwise, the next item in the Tuple will contain error
        """
        pass

    def spec(self) -> ConnectorSpecification:
        """
        Will return source specification
        """
        with open(self._spec_file, 'r') as f:
            spec_json = yaml.safe_load(f)
        print(spec_json)
        return ConnectorSpecification.model_validate(spec_json)
    
    def check(self, config: Mapping[str, Any]) -> Dict:
        """
        This will verify that the passed configuration follows a given schema and
          that connection can be established.

        Args:
            config (Mapping[str, Any]): The user-provided configuration as specified by 
            the source's spec.

        Returns:
            Dict: TODO: Should be a DatConnectionStatus object
        """
        check_succeeded, error = self.check_connection(config)
        if not check_succeeded:
            # TODO: Raise proper error
            raise

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