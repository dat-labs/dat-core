import io
import yaml
from io import StringIO
from typing import List
from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_connection_status import Status
from connectors.destinations.destination_pinecone.destination_pinecone import Pinecone
from conftest import *
from pydantic_models.dat_message import (DatMessage, DatDocumentMessage,
                                         Data, DatStateMessage, Stream,
                                         StreamState, StreamDescriptor,
                                         StreamStatus)
from pydantic_models.dat_message import Type


def _record(stream: str, data: Data) -> DatDocumentMessage:
    return DatDocumentMessage(stream=stream, data=data, emitted_at=0)

def _message(stream: str, data: Data) -> DatMessage:
    return DatMessage(type="RECORD", record=_record(stream, data))

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

    def tesxt_parse_input_stream_valid_invalid(self, ):
        # Prepare a valid input stream
        mocked_input: List[DatMessage] = [(_message("s1", data=Data(document_chunk='bar', vectors=[1, 2, 3])))]
        mocked_stdin_string = "\n".join([record.model_dump_json(exclude_unset=True) for record in mocked_input])
        mocked_stdin_string += "\n add this non-serializable string to verify the destination does not break on malformed input"

        input_stream = StringIO(mocked_stdin_string)
        assert input_stream is not None

        result_messages = list(Pinecone()._parse_input_stream(input_stream))
        assert len(result_messages) == 1
        assert result_messages[0].record.data.document_chunk == "bar"

    def test_write(self, ):
        """
        GIVEN a valid connectionSpecification JSON config
        WHEN write() is called on a valid Destination class
        THEN no error is raised
        """
        destination_config_file = "./connectors/destinations/destination_pinecone/destination_config.json"
        config = ConnectorSpecification.model_validate_json(
            open(destination_config_file).read(), )
        input_messages = [
            DatMessage(
                type=Type.RECORD,
                record=DatDocumentMessage(
                    data=Data(
                        document_chunk='foo',
                        vectors=[0.0] * 1536,
                        metadata={"meta": "Objective", "dat_source": "S3",
                                  "dat_stream": "PDF", "dat_document_entity": "DBT/DBT Overview.pdf"},
                    ),
                    emitted_at=1,
                    namespace="pytest_seeder",
                    stream="S3",
                ),
            ),
            DatMessage(
                type=Type.RECORD,
                record=DatDocumentMessage(
                    data=Data(
                        document_chunk='bar',
                        vectors=[0.0] * 1536,
                        metadata={"meta": "Arbitrary", "dat_source": "S3",
                                  "dat_stream": "PDF", "dat_document_entity": "DBT/DBT Overview.pdf"},
                    ),
                    emitted_at=2,
                    namespace="pytest_seeder",
                    stream="S3",
                ),
            ),
        ]
        docs = Pinecone().write(config=config, input_messages=input_messages)
        assert docs == len(input_messages)

    def test_run_write(self, monkeypatch):
        """
        GIVEN a valid connectionSpecification JSON config
        WHEN _run_write() is called on a valid Destination class
        THEN _run_write func should read from sys.stdin.buffer
        """
        destination_config_file = "./connectors/destinations/destination_pinecone/destination_config.json"
        config = ConnectorSpecification.model_validate_json(
            open(destination_config_file).read(), )
        # configured_catalog = DatCatalog.model_validate_json(
        #     open('./connectors/destinations/destination_pinecone/configured_catalog.json').read(), )
        first_record = DatMessage(
                type=Type.RECORD,
                record=DatDocumentMessage(
                    data=Data(
                        document_chunk='foo',
                        vectors=[0.0] * 1536,
                        metadata={"meta": "Objective", "dat_source": "S3",
                                  "dat_stream": "PDF", "dat_document_entity": "DBT/DBT Overview.pdf"},
                    ),
                    emitted_at=1,
                    namespace="pytest_seeder",
                    stream="S3",
                ),
            )
        second_record = DatMessage(
                type=Type.RECORD,
                record=DatDocumentMessage(
                    data=Data(
                        document_chunk='bar',
                        vectors=[0.0] * 1536,
                        metadata={"meta": "Arbitrary", "dat_source": "S3",
                                  "dat_stream": "PDF", "dat_document_entity": "Apple/DBT/DBT Overview.pdf"},
                    ),
                    emitted_at=2,
                    namespace="pytest_seeder",
                    stream="S3",
                ),
            )
        mocked_input: List[DatMessage] = [
            DatMessage(
                type=Type.STATE,
                state=DatStateMessage(
                    stream=Stream(
                        stream_descriptor=StreamDescriptor(name="S3", namespace="pytest_seeder"),
                        stream_state=StreamState(
                            data={},
                            stream_status=StreamStatus.STARTED
                        )
                    )
                ),
                record=first_record.record
            ),
            first_record,
            DatMessage(
                type=Type.STATE,
                state=DatStateMessage(
                    stream=Stream(
                        stream_descriptor=StreamDescriptor(name="S3", namespace="pytest_seeder"),
                        stream_state=StreamState(
                            data={},
                            stream_status=StreamStatus.STARTED
                        )
                    )
                ),
                record=second_record.record
            ),
            second_record,
            DatMessage(
                type=Type.STATE,
                state=DatStateMessage(
                    stream=Stream(
                            stream_descriptor=StreamDescriptor(name="S3", namespace="pytest_seeder"),
                            stream_state=StreamState(
                                data={"last_emitted_at": 2},
                                stream_status=StreamStatus.COMPLETED),
                        ),
                    ),
            ),
        ]
        mocked_stdin_string = "\n".join([record.model_dump_json(exclude_unset=True) for record in mocked_input])
        mocked_stdin = io.TextIOWrapper(io.BytesIO(bytes(mocked_stdin_string, "utf-8")))
        print(f"mocked_stdin: {mocked_stdin}")
        monkeypatch.setattr("sys.stdin", mocked_stdin)

        returned_write_result = Pinecone()._run_write(
            config=config,
            configured_catalog_path="./connectors/destinations/destination_pinecone/configured_catalog.json",
        )
        for result in returned_write_result:
            print(f"result: {result}")
            assert isinstance(result, DatMessage)
            assert result.type == Type.STATE
