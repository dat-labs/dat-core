from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Tuple, Union
from utils import schema_validate

class SourceBase(ABC):
    """
    Base abstract Class for all sources
    """
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

    def spec(self):
        """
        Will return source specification
        """
        pass
    
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

    def discover(self, config: Mapping[str, Any]) -> Dict:
        """
        Should publish a connectors capabilities i.e it's catalog

        Args:
            config (Mapping[str, Any]): The user-provided configuration as specified by
              the source's spec.

        Returns:
            Dict: TODO: Should return a DatCatalog object
        """
        pass

    def read(
        self,
        config: Mapping[str, Any],
        catalog: Mapping[str, Any],
        state: Optional[Union[List[Dict], MutableMapping[str, Any]]] = None,
    ) -> Iterator[Dict]:
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