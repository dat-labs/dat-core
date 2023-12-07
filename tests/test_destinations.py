import os
from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_connection_status import Status
from connectors.destinations.destination_pinecone.destination_pinecone import DestinationPinecone
from conftest import *


def test_destinations_spec():
    """
    GIVEN None
    WHEN spec() is called on a valid Destination class
    THEN spec stated in ./specs/ConnectorSpecification.yml is returned
    """
    spec = DestinationPinecone().spec()
    with open('./connectors/destinations/destination_pinecone/specs.yml') as yaml_in:
        schema = yaml.safe_load(yaml_in)
        assert schema == spec

def test_destinations_check():
    """
    GIVEN a valid connectionSpecification JSON config
    WHEN check() is called on a valid Destination class
    THEN no error is raised
    """
    destination_config_file = "./connectors/destinations/destination_pinecone/destination_config.json"
    check = DestinationPinecone().check(
        config=ConnectorSpecification.model_validate_json(
            open(destination_config_file).read()),)
    assert check.status == Status.SUCCEEDED
