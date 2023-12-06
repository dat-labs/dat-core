from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_connection_status import DatConnectionStatus, Status
from connectors.generators.base import OpenAI
from conftest import *


def test_generators_spec():
    """
    GIVEN None
    WHEN spec() is called on a valid Generator class
    THEN spec stated in ./specs/ConnectorSpecification.yml is returned
    """
    
    spec = OpenAI().spec()
    with open('./connectors/generators/specs.yml') as yaml_in:
        schema = yaml.safe_load(yaml_in)
        assert schema == spec


def test_generators_check():
    """
    GIVEN a valid connectionSpecification JSON config
    WHEN check() is called on a valid Generator class
    THEN no error is raised
    """
    check = OpenAI().check(config=ConnectorSpecification.model_validate_json(
            open('generator_config.json').read()),)
    assert check.status == Status.SUCCEEDED

def test_generators_generate():
    """
    GIVEN a valid connectionSpecification JSON config
    WHEN check() is called on a valid Generator class
    THEN no error is raised
    """