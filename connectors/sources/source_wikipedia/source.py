import os
from typing import Tuple, Any, List
from connectors.sources.base import SourceBase
from connectors.sources.stream import Stream
from connectors.sources.source_wikipedia.streams import ContentSearch
from pydantic_models.connector_specification import ConnectorSpecification
from auth.core import NoAuth


class Wikipedia(SourceBase):
    """
    Wikipedia as a source
    """
    _spec_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'specs.yml')

    def check_connection(self, config: ConnectorSpecification) -> Tuple[bool, Any | None]:
        """
        Check whether the user provided config is able to make a connection 
        to Wikipedia or not
        """
        return True, 'No Authentication required'
    
    def streams(self, config: ConnectorSpecification) -> List[Stream]:
        """
        Return list of available streams in Zendesk

        Args:
            config (Mapping[str, Any]): The user-provided configuration as specified by
              the source's spec.
        Returns:
            List[Stream]: No need to explain
        """
        auth = NoAuth()
        return [ContentSearch(config=config, authenticator=auth)]
    

if __name__ == '__main__':
    config = ConnectorSpecification(connectionSpecification={})
    catalog = Wikipedia().discover(config=config)
    print(catalog)
    doc_generator = Wikipedia().read(config=config, catalog=catalog)
    for doc in doc_generator:
        print(doc)