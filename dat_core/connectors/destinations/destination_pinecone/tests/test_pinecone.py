import io
import yaml
from typing import List
from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_connection_status import Status
from connectors.destinations.destination_pinecone.destination_pinecone import Pinecone
from conftest import *
from pydantic_models.dat_message import (DatMessage, DatDocumentMessage,
                                         Data, DatStateMessage,
                                         StreamState, StreamStatus,
                                         DatDocumentStream, Type)
from pydantic_models.dat_catalog import DatCatalog

class TestPinecone:

    def test_spec(self, ):
        """
        GIVEN None
        WHEN spec() is called on a valid Destination class
        THEN spec stated in ./specs/ConnectorSpecification.yml is returned
        """
        spec = Pinecone().spec()
        with open('./connectors/destinations/destination_pinecone/specs.yml') as yaml_in:
            schema = yaml.safe_load(yaml_in)
            assert schema == spec

    def test_check(self, ):
        """
        GIVEN a valid connectionSpecification JSON config
        WHEN check() is called on a valid Destination class
        THEN no error is raised
        """
        destination_config_file = "./connectors/destinations/destination_pinecone/destination_config.json"
        config = ConnectorSpecification.model_validate_json(
            open(destination_config_file).read(), )
        check = Pinecone().check(
            config=config)
        print(check)
        assert check.status == Status.SUCCEEDED

    def test_write(self, ):
        """
        GIVEN a valid connectionSpecification JSON config
        WHEN write() is called on a valid Destination class
        THEN no error is raised
        """
        destination_config_file = "./connectors/destinations/destination_pinecone/destination_config.json"
        config = ConnectorSpecification.model_validate_json(
            open(destination_config_file).read(), )
        configured_catalog = DatCatalog.model_validate_json(
            open('./connectors/destinations/destination_pinecone/configured_catalog.json').read(), )
        first_record = DatMessage(
                type=Type.RECORD,
                record=DatDocumentMessage(
                    data=Data(
                        document_chunk='foo',
                        vectors=[0.1] * 1536,
                        metadata={"meta": "Objective", "dat_source": "S3",
                                  "dat_stream": "PDF", "dat_document_entity": "DBT/DBT Overview.pdf"},
                    ),
                    emitted_at=1,
                    namespace="pytest_seeder",
                    stream=DatDocumentStream(
                        name="S3",
                        namespace="pytest_seeder",
                        sync_mode="incremental",
                    ),
                ),
            )
        second_record = DatMessage(
                type=Type.RECORD,
                record=DatDocumentMessage(
                    data=Data(
                        document_chunk='bar',
                        vectors=[1.0] * 1536,
                        metadata={"meta": "Arbitrary", "dat_source": "S3",
                                  "dat_stream": "PDF", "dat_document_entity": "Apple/DBT/DBT Overview.pdf"},
                    ),
                    emitted_at=2,
                    namespace="pytest_seeder",
                    stream=DatDocumentStream(
                        name="S3",
                        namespace="pytest_seeder",
                        sync_mode="incremental",
                    )
                ),
            )
        mocked_input: List[DatMessage] = [
            first_record,
            second_record,
        ]
        docs = Pinecone().write(
            config=config,
            configured_catalog=configured_catalog,
            input_messages=mocked_input
        )
        for doc in docs:
            print(f"doc: {doc}")
            assert isinstance(doc, DatMessage)

    def test_write_state_started(self, ):
        """
        GIVEN a valid connectionSpecification JSON config
        WHEN write() is called on a valid Destination class
        THEN no error is raised
        """
        destination_config_file = "./connectors/destinations/destination_pinecone/destination_config.json"
        config = ConnectorSpecification.model_validate_json(
            open(destination_config_file).read(), )
        configured_catalog = DatCatalog.model_validate_json(
            open('./connectors/destinations/destination_pinecone/configured_catalog.json').read(), )
        first_record = DatMessage(
                type=Type.RECORD,
                record=DatDocumentMessage(
                    data=Data(
                        document_chunk='foo',
                        vectors=[1.0] * 1536,
                        metadata={"meta": "Objective", "dat_source": "S3",
                                  "dat_stream": "PDF", "dat_document_entity": "DBT/DBT Overview.pdf"},
                    ),
                    emitted_at=1,
                    namespace="pytest_seeder",
                    stream=DatDocumentStream(
                        name="S3",
                        namespace="pytest_seeder",
                        sync_mode="incremental",
                    ),
                ),
            )
        second_record = DatMessage(
                type=Type.RECORD,
                record=DatDocumentMessage(
                    data=Data(
                        document_chunk='bar',
                        vectors=[1.1] * 1536,
                        metadata={"meta": "Arbitrary", "dat_source": "S3",
                                  "dat_stream": "PDF", "dat_document_entity": "Apple/DBT/DBT Overview.pdf"},
                    ),
                    emitted_at=2,
                    namespace="pytest_seeder",
                    stream=DatDocumentStream(
                        name="GCS",
                        namespace="pytest_seeder",
                        sync_mode="incremental",
                    )
                ),
            )
        mocked_input: List[DatMessage] = [
            DatMessage(
                type=Type.STATE,
                state=DatStateMessage(
                    stream=DatDocumentStream(
                        name="S3",
                        namespace="pytest_seeder",
                        sync_mode="incremental",
                    ),
                    stream_state=StreamState(
                        data={},
                        stream_status=StreamStatus.STARTED
                    )
                ),
                record=first_record.record
            ),
            first_record,
            DatMessage(
                type=Type.STATE,
                state=DatStateMessage(
                    stream=DatDocumentStream(
                        name="GCS",
                        namespace="pytest_seeder",
                        sync_mode="incremental",
                    ),
                    stream_state=StreamState(
                        data={},
                        stream_status=StreamStatus.STARTED
                    )
                ),
                record=second_record.record
            ),
            second_record,
            DatMessage(
                type=Type.STATE,
                state=DatStateMessage(
                    stream=DatDocumentStream(
                        name="S3",
                        namespace="pytest_seeder",
                        sync_mode="incremental",
                    ),
                    stream_state=StreamState(
                        data={"last_emitted_at": 2},
                        stream_status=StreamStatus.COMPLETED
                    )
                ),
            ),
        ]
        docs = Pinecone().write(
            config=config,
            configured_catalog=configured_catalog,
            input_messages=mocked_input
        )
        for doc in docs:
            print(f"doc: {doc}")
            assert isinstance(doc, DatMessage)
