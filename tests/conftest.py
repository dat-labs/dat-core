import json
import yaml
from jsonschema import validate
import pytest
from connectors.destinations.destination import Destination


@pytest.fixture(name="destination")
def destination_fixture(mocker) -> Destination:

    mocker.patch("connectors.destinations.Destination.__abstractmethods__", set())
    return Destination()
