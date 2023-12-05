from typing import Any, Dict, Iterable, List, Mapping, Optional
from connectors.sources.stream import Stream
from pydantic_models.connector_specification import ConnectorSpecification


class ZendeskStream(Stream):
    """
    Base class for a Zendesk stream
    """
    def read_records(self,
        config: ConnectorSpecification,
        sync_mode: str,
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

class Agent(ZendeskStream):
    """
    Stream class for a Zendesk Agent
    """
    def request_params(self, stream_state: Optional[Mapping[str, Any]], next_page_token: Optional[str]) -> Dict:
        pass

    def send_request(self, params: Dict) -> Iterable[Dict]:
        pass

    def parse_response(self, response: Iterable[Dict]) -> Iterable[Dict]:
        pass