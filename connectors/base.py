from abc import ABC, abstractmethod
from typing import (Any, Dict, Mapping, Optional, Tuple)
import yaml
from utils import schema_validate
from pydantic_models.connector_specification import ConnectorSpecification


class ConnectorBase(ABC):

    _spec_file = None

    @abstractmethod
    def check_connection(self, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        Based on the given config, it will check if connection to
        a source/generator/desitnation can be established.

        Args:
            config (Mapping[str, Any]): The user-provided configuration as specified by
              the source's spec.

        Returns:
            Tuple[bool, Optional[Any]]: If the bool is True, then connection is established. The next item in the Tuple will either house a connection error or proof of connection.
        """
        pass

    def spec(self) -> Dict:
        """
        Will return source specification
        """
        with open(self._spec_file, 'r') as f:
            spec_json = yaml.safe_load(f)
        return spec_json

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
        assert schema_validate(
            json_str=config.model_dump_json(),
            schema_yml_path=self._spec_file,
        )
        check_succeeded, error = self.check_connection(config)
        if not check_succeeded:
            # TODO: Raise proper error
            raise Exception('Raise proper exception')
