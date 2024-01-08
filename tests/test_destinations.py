import os
import argparse
import yaml
from io import StringIO
from typing import Any, List, Union
from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_connection_status import Status
from connectors.destinations.destination_pinecone.destination_pinecone import Pinecone
from conftest import *
from pydantic_models.dat_message import DatMessage, DatDocumentMessage, Data
from pydantic_models.dat_connection_status import DatConnectionStatus
from connectors.destinations.destination import Destination
from pydantic_models.dat_message import Type


def _record(stream: str, data: Data) -> DatDocumentMessage:
    return DatDocumentMessage(stream=stream, data=data, emitted_at=0)

def _message(stream: str, data: Data) -> DatMessage:
    return DatMessage(type="RECORD", record=_record(stream, data))

def _wrapped(
    msg: Union[DatDocumentMessage, ConnectorSpecification, DatConnectionStatus]
) -> DatMessage:
    if isinstance(msg, DatDocumentMessage):
        return DatMessage(type=Type.RECORD, record=msg)
    elif isinstance(msg, DatConnectionStatus):
        return DatMessage(type=Type.CONNECTION_STATUS, connectionStatus=msg)
    elif isinstance(msg, ConnectorSpecification):
        return DatMessage(type=Type.SPEC, spec=msg)
    else:
        raise Exception(f"Invalid Dat Message: {msg}")

class TestDestination:

    def test_destination_spec(self, ):
        """
        GIVEN None
        WHEN spec() is called on a valid Destination class
        THEN spec stated in ./specs/ConnectorSpecification.yml is returned
        """
        spec = Pinecone().spec()
        with open('./connectors/destinations/destination_pinecone/specs.yml') as yaml_in:
            schema = yaml.safe_load(yaml_in)
            assert schema == spec

    def test_destination_check(self, ):
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

    def test_destination_parse_input_stream_valid_invalid(self, ):
        # Prepare a valid input stream
        mocked_input: List[DatMessage] = [(_message("s1", data=Data(document_chunk='bar', vectors=[1, 2, 3])))]
        mocked_stdin_string = "\n".join([record.json(exclude_unset=True) for record in mocked_input])
        mocked_stdin_string += "\n add this non-serializable string to verify the destination does not break on malformed input"

        input_stream = StringIO(mocked_stdin_string)
        assert input_stream is not None

        result_messages = list(Pinecone()._parse_input_stream(input_stream))
        assert len(result_messages) == 1
        assert result_messages[0].record.data.document_chunk == "bar"

    def test_destination_write(self, ):
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
