from abc import ABC, abstractmethod
from typing import (Any, Dict, Optional, Tuple)
import yaml
from utils import schema_validate
from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_connection_status import DatConnectionStatus, Status


class ConnectorBase(ABC):

    _spec_file = None

    @abstractmethod
    def check_connection(self, config: ConnectorSpecification) -> Tuple[bool, Optional[Any]]:
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

    def check(self, config: ConnectorSpecification) -> Dict:
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
            instance=config.model_dump(),
            schema_yml_path=self._spec_file,
        )
        # e_o_p_o_c: error or proof of connection
        check_succeeded, e_o_p_o_c = self.check_connection(config)
        return DatConnectionStatus(
            status=Status.SUCCEEDED if check_succeeded else Status.FAILED,
            message=str(e_o_p_o_c),
        )
