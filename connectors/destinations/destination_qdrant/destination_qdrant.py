import os
from typing import Any, Tuple, Optional, Mapping, Iterable
from connectors.destinations.destination import Destination
from pydantic_models.connector_specification import ConnectorSpecification
from connectors.destinations.destination_qdrant.seeder import QdrantSeeder
from connectors.destinations.vector_db_helpers.data_processor import DataProcessor
from pydantic_models.dat_catalog import DatCatalog
from pydantic_models.dat_message import DatMessage, Type, DatDocumentMessage, Data
from pydantic_models.dat_document_stream import SyncMode, DatDocumentStream


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

    def write(self, config: Mapping[str, Any], configured_catalog: DatCatalog, input_messages: Iterable[DatMessage]) -> Iterable[DatMessage]:
        self._init_seeder(config)
        processor = DataProcessor(config, self.seeder, BATCH_SIZE)
        yield from processor.processor(configured_catalog, input_messages)

if __name__ == '__main__':
    destination_config_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'destination_config.json')
    config = ConnectorSpecification.model_validate_json(
            open(destination_config_file).read(), )
    configured_catalog = DatCatalog.model_validate_json(
            open('./connectors/destinations/destination_qdrant/configured_catalog.json').read(), )
    print(config)
    _spec = Qdrant().spec()
    print(f"spec: {_spec}")
    _dest = Qdrant().check(config=config)
    print(f"destination check: {_dest}")
    docs = Qdrant().write(config=config,configured_catalog=configured_catalog , input_messages=[
        DatMessage(
            type=Type.RECORD,
            record=DatDocumentMessage(
                data=Data(
                    document_chunk='foo',
                    vectors=[0.0] * 1536,
                    metadata={"meta": "Objective", "dat_source": "S3", "dat_stream": "PDF", "dat_document_entity": "DBT/DBT Overview.pdf"},
                ),
                emitted_at=1,
                namespace="Seeder",
                stream=DatDocumentStream(
                    name="S3",
                    namespace="Seeder",
                    sync_mode=SyncMode.INCREMENTAL),
            ),
        ),
        DatMessage(
            type=Type.RECORD,
            record=DatDocumentMessage(
                data=Data(
                    document_chunk='bar',
                    vectors=[0.0] * 1536,
                    metadata={"meta": "Arbitrary", "dat_source": "S3", "dat_stream": "PDF", "dat_document_entity": "DBT/DBT Overview.pdf"},
                ),
                emitted_at=2,
                namespace="Seeder",
                stream=DatDocumentStream(
                    name="S3",
                    namespace="Seeder",
                    sync_mode=SyncMode.INCREMENTAL),
            ),
        ),
    ])
    for doc in docs:
        print(f"doc: {doc}")
