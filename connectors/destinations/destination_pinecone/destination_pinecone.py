import json
import os
import itertools
import pinecone
from connectors.destinations.destination import Destination
from typing import Any, Iterable, Mapping, Tuple, Optional, Generator, TypeVar, List
import pinecone
from pydantic_models.connector_specification import ConnectorSpecification, DestinationSyncMode
from pydantic_models.dat_catalog import DatCatalog
from pydantic_models.dat_message import DatMessage, Type, DatDocumentMessage, Data
from connectors.destinations.destination_pinecone.seeder import PineconeSeeder, Chunk
from connectors.destinations.vector_db_helpers.data_processor import DataProcessor


BATCH_SIZE = 1000


class DestinationPinecone(Destination):

    _spec_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'specs.yml')

    def _init_seeder(self, config: Mapping[str, Any]) -> None:
        self.seeder = PineconeSeeder(config, config.connectionSpecification.get('embedding_dimensions'))

    def check_connection(self, config: ConnectorSpecification) -> Tuple[bool, Optional[Any]]:
        self._init_seeder(config)
        try:
            check, desc = self.seeder.check()
            return (check, desc)
        except Exception as e:
            return (False, e)

    def write(self, config: Mapping[str, Any], input_messages: Iterable[DatMessage]) -> Iterable[DatMessage]:
        # vectors = []
        # for input_message in input_messages:
        #     vectors.append((input_message.record.data.document_chunk, input_message.record.data.vectors))
        # self._insert_data_to_pinecone(vectors)
        self._init_seeder(config)
        processor = DataProcessor(config, self.seeder, BATCH_SIZE, False)
        yield from processor.processor(config, input_messages)

    # def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
    #     return ConnectorSpecification(
    #         supportsIncremental=True,
    #         supported_destination_sync_modes=[
    #             DestinationSyncMode.upsert, DestinationSyncMode.append, DestinationSyncMode.replace],
    #         connectionSpecification={"pinecone_api_key": {"type": "string", "title": "Pinecone API Key", "description": "Pinecone API Key", "minLength": 1, "examples": ["1234567890"]},
    #                                  "pinecone_index": {"type": "string", "title": "Pinecone Index", "description": "Pinecone Index", "minLength": 1, "examples": ["my_index"]},
    #                                  "pinecone_environment": {"type": "string", "title": "Pinecone Environment", "description": "Pinecone Environment", "minLength": 1, "examples": ["us-west1-gcp"]},
    #                                  "pinecone_batch_size": {"type": "integer", "title": "Pinecone Batch Size", "description": "Pinecone Batch Size", "minimum": 1, "maximum": 10000, "examples": [1000]},
    #                                  "pinecone_index_timeout": {"type": "integer", "title": "Pinecone Index Timeout", "description": "Pinecone Index Timeout", "minimum": 1, "maximum": 10000, "examples": [1000]}},
    #     )


if __name__ == '__main__':
    destination_config_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'destination_config.json')
    config = ConnectorSpecification.model_validate_json(
        open(destination_config_file).read(), )
    # config = ConnectorSpecification.parse_obj(
    #     json.loads(open(destination_config_file).read()))
    print(config)
    _spec = DestinationPinecone().spec()
    print(f"spec: {_spec}")
    _dest = DestinationPinecone().check(config=config)
    print(f"destination check: {_dest}")

    messages = DestinationPinecone().write(config=config, input_messages=[
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
                stream="S3",
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
                stream="S3",
            ),
        ),
    ])
