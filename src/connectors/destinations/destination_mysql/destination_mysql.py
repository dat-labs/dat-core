from typing import Any, Tuple, Iterable, Mapping
import os
import mysql.connector
from connectors.destinations.destination import Destination
from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_message import DatMessage


class DestinationMysql(Destination):

    _spec_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'specs.yml')
    
    def check_connection(self, config: ConnectorSpecification) -> Tuple[bool, Any]:
        """
        Check whether the user provided config is able to make a connection 
        to MySQL or not
        """
        try:
            conn = mysql.connector.connect(
                host=config.connectionSpecification['host'],
                user=config.connectionSpecification['user'],
                password=config.connectionSpecification['password'],
                database=config.connectionSpecification['database'],
                port=config.connectionSpecification['port']
            )
            conn.close()
        except mysql.connector.Error as err:
            return False, err
        return True, conn

    def write(self, config: Mapping[str, Any], input_messages: Iterable[DatMessage]) -> Iterable[DatMessage]:
        """
        Write the input messages to MySQL
        """
