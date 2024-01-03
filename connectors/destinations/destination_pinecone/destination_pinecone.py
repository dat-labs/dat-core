import os
import pinecone
from connectors.destinations.destination import Destination
from typing import Any, Iterable, Mapping, Tuple, Optional
import pinecone
from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_catalog import DatCatalog
from pydantic_models.dat_message import DatMessage


class DestinationPinecone(Destination):

    _spec_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'specs.yml')

    def check_connection(self, config: ConnectorSpecification) -> Tuple[bool, Optional[Any]]:
        index = config.connectionSpecification.get('pinecone_index')
        pinecone_environment = config.connectionSpecification.get('pinecone_environment')

        pinecone.init(api_key=config.connectionSpecification.get('pinecone_api_key'), environment=pinecone_environment)
        embedding_dimensions = 1536

        try:
            indexes = pinecone.list_indexes()
            if index not in indexes:
                return False, f"Index {index} does not exist in environment {pinecone_environment}."
            description = pinecone.describe_index(index)
            if description.dimension != embedding_dimensions:
                return (False,
                (f"Index {index} has dimension {description.dimension} "
                f"but configured dimension is {embedding_dimensions}."))
        except Exception as e:
            raise e
        return True, description
    
    def write(self, config: Mapping[str, Any], configured_catalog: DatCatalog, input_messages: Iterable[DatMessage]) -> Iterable[DatMessage]:
        return super().write(config, configured_catalog, input_messages)


if __name__ == '__main__':
    # import pdb;pdb.set_trace()
    destination_config_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'destination_config.json')
    config=ConnectorSpecification.model_validate_json(
            open(destination_config_file).read())
    _dest = DestinationPinecone().check(config=config)
    print(f"destination check: {_dest}")