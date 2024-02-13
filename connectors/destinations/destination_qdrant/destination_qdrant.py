import os
from typing import Any, Tuple, Optional, Mapping
from connectors.destinations.destination import Destination
from pydantic_models.connector_specification import ConnectorSpecification
from connectors.destinations.destination_qdrant.seeder import QdrantSeeder
from connectors.destinations.vector_db_helpers.data_processor import DataProcessor


BATCH_SIZE = 1000

class Qdrant(Destination):
    
    _spec_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'specs.yml')

    def _init_seeder(self, config: Mapping[str, Any]) -> None:
        self.seeder = QdrantSeeder(config, config.connectionSpecification.get('embedding_dimensions'))

    def check_connection(self, config: ConnectorSpecification) -> Tuple[bool, Optional[Any]]:
        self._init_seeder(config)
        try:
            check, desc = self.seeder.check()
            return (check, desc)
        except Exception as e:
            return (False, e)

    def write(self, config: Mapping[str, Any], configured_catalog: Any, input_messages: Any) -> Any:
        self._init_seeder(config)
        processor = DataProcessor(config, self.seeder, BATCH_SIZE, False)
        yield from processor.processor(configured_catalog, input_messages)

if __name__ == '__main__':
    destination_config_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'destination_config.json')
    config = ConnectorSpecification.model_validate_json(
            open(destination_config_file).read(), )
    _spec = Qdrant().spec()
    print(f"spec: {_spec}")
    _dest = Qdrant().check(config=config)
    print(f"destination check: {_dest}")
