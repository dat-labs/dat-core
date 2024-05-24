from abc import ABC, abstractmethod
from typing import (Any, Dict, Optional, Tuple)
import jsonref
from dat_core.pydantic_models import (
    ConnectorSpecification,
    DatConnectionStatus,
    Status,
)


class ConnectorBase(ABC):

    _spec_class = ConnectorSpecification

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

    def spec(self) -> Dict:
        """
        Will return source specification
        """
        _spec = self._spec_class.model_json_schema()
        _resolved_spec =  jsonref.loads(jsonref.dumps(_spec))
        # _conn_spec = _resolved_spec['properties']['connection_specification']
        # for _schema in _conn_spec['allOf']:
        #     for k,v in _schema.items():
        #         _conn_spec[k] = v
        # del _conn_spec['allOf']
        # del _resolved_spec['$defs']
        return _resolved_spec



    def check(self, config: ConnectorSpecification) -> DatConnectionStatus:
        """
        This will verify that the passed configuration follows a given schema and
          that connection can be established.

        Args:
            config (Mapping[str, Any]): The user-provided configuration as specified by 
            the source's spec.

        Returns:
            DatConnectionStatus
        """
        # e_o_p_o_c: error or proof of connection
        check_succeeded, e_o_p_o_c = self.check_connection(config)
        return DatConnectionStatus(
            status=Status.SUCCEEDED if check_succeeded else Status.FAILED,
            message=str(e_o_p_o_c),
        )
