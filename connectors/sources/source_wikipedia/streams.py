import requests
import time
from lxml import html
from typing import Any, Dict, Iterable, List, Mapping, Optional
from connectors.sources.stream import Stream
from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_catalog import SyncMode
from pydantic_models.dat_message import DatMessage, Type, DatDocumentMessage, Data
class WikipediaStream(Stream):
    """
    Base class for a Wikipedia stream
    """
    def __init__(self, config: ConnectorSpecification, schema: Optional[Mapping[str, Any]]=None, **kwargs: Mapping[str, Any]) -> None:
        self.config = config
        self._schema = schema
        self.authenticator = kwargs.get('authenticator', None)
    
    def read_records(self,
        config: ConnectorSpecification,
        sync_mode: SyncMode,
        cursor_field: List[str] | None = None,
        stream_state: Mapping[str, Any] | None = None
    ) -> Iterable[Dict]:
        """
        Will fetch data from the stream. It also supports pagination

        Args:
            config (ConnectorSpecification): The user-provided configuration as specified by
              the source's spec. 
            sync_mode (str): incremental|full
            cursor_field (List[str] | None, optional): The point from which data is to be fetched. Defaults to None.
            stream_state (Mapping[str, Any] | None, optional): Last watermark for the data fetched. Defaults to None.

        Returns:
            Iterable[Dict]: A generator or a list of dict data
        """
        next_page_token = None
        while True:
            params = self.request_params(
                stream_state=stream_state,
                next_page_token=next_page_token,
            )
            response = self.send_request(params)
            for record in self.parse_response(response):
                yield record

            next_page_token = self.next_page_token(response, current_page_token=next_page_token)
            if not next_page_token:
                break

class ContentSearch(WikipediaStream):
    """
    Stream class for a Wikipedia Agent
    """
    _endpoint = 'https://en.wikipedia.org/w/api.php'

    def request_params(self, stream_state: Optional[Mapping[str, Any]], next_page_token: Optional[str]) -> Dict:
        """
        Any optional parameter that has to be passed to send_request

        Args:
            stream_state (Optional[Mapping[str, Any]]): Last know state of the stream
            next_page_token (Optional[str]): If available

        Returns:
            Dict: request params as a dict
        """
        params = {
            'action': 'parse',
            'format': 'json',
            'page': 'Quantum Computing',
            'prop': 'text',
            'redirects':''
        }
        return params

    def send_request(self, params: Dict) -> Iterable[Dict]:
        """
        Send a HTTP request with the given params and 
        available authenticator
        """
        resp = requests.get(self._endpoint, params=params, headers=self.authenticator.get_auth_header())
        print(f'Calling {self._endpoint}')
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception('Raise an Authentication error') #TODO
        
    def parse_response(self, response: Iterable[Dict]) -> Iterable[Dict]:
        """
        Parse the response based on available schema
        TODO: Integrate parsing based on schema information
        """
        raw_html = response['parse']['text']['*']
        document = html.document_fromstring(raw_html)
        text = ''
        for p in document.xpath('//p'):
            text = p.text_content() + '\n'
            dat_msg = DatMessage(
                type=Type.RECORD,
                record=DatDocumentMessage(
                    stream=self.name,
                    data=Data(document_chunk=text, metadata=None),
                    emitted_at=int(time.time())),
            )
            yield dat_msg
    
    def next_page_token(self, response: Iterable[Dict], current_page_token: Optional[str]) -> str:
        """
        TODO: To be implemented

        Args:
            response (Iterable[Dict]): _description_
            current_page_token (Optional[str]): _description_

        Returns:
            str: _description_
        """
        return None