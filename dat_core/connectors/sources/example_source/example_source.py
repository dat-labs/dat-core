import os
from typing import Any, Dict, List, Mapping, Optional, Tuple
from dat_core.connectors.sources.base import SourceBase
from dat_core.connectors.sources.stream import Stream
from dat_core.connectors.sources.example_source.streams import Agent
from dat_core.pydantic_models.connector_specification import ConnectorSpecification
from dat_core.pydantic_models.dat_catalog import SyncMode
from auth.token_authenticator import BasicHttpAuthenticator

class Zendesk(SourceBase):

    """
    Example source
    """
    _spec_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'specs.yml')
    _catalog_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'catalog.yml')

    def check_connection(self, config: Mapping[str, Any]) -> Tuple[bool, Any | None]:
        """
        Check whether the user provided config is able to make a connection 
        to Zendesk or not
        """
        auth = BasicHttpAuthenticator(
            username=config.connectionSpecification['zendesk_username'],
            password=config.connectionSpecification['zendesk_password']
            )
        agent_stream = Agent(config, authenticator=auth)
        try:
            for record in agent_stream.read_records(config=config, sync_mode=SyncMode.incremental):
                print(record)
        except: #TODO: Catch an AuthenticationError
            return False, False
        
        return (True, True)
    
    def streams(self, config: Mapping[str, Any], json_schemas: Mapping[str, Mapping[str, Any]]=None) -> List[Stream]:
        """
        Return list of available streams in Zendesk

        Args:
            config (Mapping[str, Any]): The user-provided configuration as specified by
              the source's spec.
            json_schemas (Mapping[str, Mapping[str, Any]]): List of json schemas with each item a dictionary
                with it's key as stream name
        Returns:
            List[Stream]: No need to explain
        """
        return [Agent(config)]

if __name__ == '__main__':
    import os
    # config_json = Zendesk().spec()
    # print(config_json)
    config = ConnectorSpecification(
        connectionSpecification={'zendesk_username': os.environ.get('zendesk_username'), 'zendesk_password': os.environ.get('zendesk_password')}
    )
    print(config.model_dump_json())
    Zendesk().check(config=config)
    print(Zendesk().discover(config=config))
    