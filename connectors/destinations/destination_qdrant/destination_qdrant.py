import os
from typing import Any, Tuple
import qdrant_client
from connectors.destinations.destination import Destination
from pydantic_models.connector_specification import ConnectorSpecification


class Qdrant(Destination):
    
    _spec_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'specs.yml')
    
    def check_connection(self, config: ConnectorSpecification) -> Tuple[bool, Any]:
        """
        Check connection to Qdrant
        """
        try:
            conn = qdrant_client.QdrantClient(host=config.connectionSpecification['host'],
                                              port=config.connectionSpecification['port'])
            conn.close()
        except Exception as err:
            return False, err
        return True, conn
