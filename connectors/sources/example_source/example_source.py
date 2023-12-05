import os
from typing import Any, Dict, List, Mapping, Optional, Tuple
from connectors.sources.base import SourceBase
from connectors.sources.stream import Stream
from connectors.sources.example_source.streams import Agent
from pydantic_models.connector_specification import ConnectorSpecification
class Zendesk(SourceBase):

    """
    Example source
    """
    _spec_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'specs.yml')

    def check_connection(self, config: Mapping[str, Any]) -> Tuple[bool, Any | None]:
        return (True, True)
    
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Return list of available streams in Zendesk

        Args:
            config (Mapping[str, Any]): The user-provided configuration as specified by
              the source's spec.
        Returns:
            List[Stream]: No need to explain
        """
        return [Agent(config)]

if __name__ == '__main__':
    config = ConnectorSpecification(
        connectionSpecification={'zendesk_username': '', 'zendesk_password': ''}
    )
    print(Zendesk().discover(config=config))