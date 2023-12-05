from abc import ABC, abstractmethod
from typing import (Any, Dict, Mapping, Optional, Tuple)
import yaml
from pydantic_models.connector_specification import ConnectorSpecification


class ConnectorBase(ABC):

    _spec_file = None

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
