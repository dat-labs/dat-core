from connectors.generators.spec import main as spec
from conftest import *


def test_generators_spec():
    """
    GIVEN None
    WHEN ./connectors/generators/spec.py is called
    THEN spec stated in ./specs/ConnectorSpecification.yml is returned
    """
    _r = spec()
    with open('./specs/ConnectorSpecification.yml') as yaml_in:
        schema = yaml.safe_load(yaml_in)
        assert schema == _r


def test_generators_check():
    """
    GIVEN a valid connectionSpecification JSON config
    WHEN ./connectors/generators/spec.py is called
    THEN spec stated in ./specs/ConnectorSpecification.yml is returned
    """
    _r = spec()
    with open('./specs/ConnectorSpecification.yml') as yaml_in:
        schema = yaml.safe_load(yaml_in)
        assert schema == _r
