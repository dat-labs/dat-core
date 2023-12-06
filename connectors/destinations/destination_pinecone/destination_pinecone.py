import os
import json
import pinecone
from connectors.destinations.destination import Destination
from typing import Any, Mapping, Tuple, Iterable
import pinecone
from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_message import DatMessage
from pydantic_models.dat_catalog import DatCatalog


class DestinationPinecone(Destination):

    _spec_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'specs.yml')

    def check_connection(self, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        with open(config) as config_file:
            config = json.loads(config_file.read())
        index = config.get('connectionSpecification').get('pinecone_index')
        pinecone_environment = config.get('connectionSpecification').get('pinecone_environment')

        pinecone.init(api_key=config.get('connectionSpecification').get('pinecone_api_key'), environment=pinecone_environment)
        embedding_dimensions = 1536

        try:
            indexes = pinecone.list_indexes()
            if index not in indexes:
                return False, f"Index {index} does not exist in environment {pinecone_environment}."
            print(f"Index {index} exists in environment {pinecone_environment}.")
            description = pinecone.describe_index(index)
            print(f"Index {index} has status {description.status}.")
            if description.dimension != embedding_dimensions:
                return (False,
                (f"Index {index} has dimension {description.dimension} "
                f"but configured dimension is {embedding_dimensions}."))
        except Exception as e:
            raise e
        return True, True


if __name__ == '__main__':
    # import pdb;pdb.set_trace()
    config = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'destination_config.json')
    _dest = DestinationPinecone().check(config=config)
    print(f"destination check: {_dest}")
