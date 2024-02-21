from typing import Dict, List, Optional, Iterable, Mapping, Any
from abc import ABC, abstractmethod, abstractclassmethod
from dat_core.pydantic_models.connector_specification import ConnectorSpecification
from dat_core.pydantic_models.dat_document_stream import DatDocumentStream, SyncMode
from dat_core.pydantic_models.dat_message import DatMessage
from dat_core.pydantic_models.stream_metadata import StreamMetadata

def to_snake_case(_str):
    """
    Given a camel_case string, convert it
    to snake case.
    E.g
    ThisIsCamel ---> this_is_camel
    thisIsCamel ---> this_is_camel
    """
    import re
    a = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
    return a.sub(r'_\1', _str).lower()

class Stream(ABC):
    """
    Base abstract class for a Dat Stream
    """
    @classmethod
    @property
    def name(cls) -> str:
        """
        Returns the name of the stream. Ideally it should be a
        camel case string matching the class name.
        """
        # TODO: Make a function for camel case
        return to_snake_case(cls.__name__)

    @property
    def sync_mode(self) -> SyncMode:
        # TODO: Fix return
        return SyncMode.INCREMENTAL
    
    @property
    def json_schema(self) -> Mapping[str, Any]:
        return self._schema
    
    def as_pydantic_model(self) -> DatDocumentStream:
        return DatDocumentStream(
            name=self.name,
            namespace='test_1',
            sync_mode=self.sync_mode,
            json_schema=self.json_schema,
        )
    
    def get_schema_json(self) -> Dict:
        """
        Get the schema by either reading from the catalog.yml or some
        custom implementation

        Returns:
            Dict: schema of the stream response
        """
        # Default behavior. Otherwise one could have custom implementation
        return self.json_schema
    
    @abstractmethod
    def get_metadata(self, document_chunk: str, data_entity: str) -> StreamMetadata:
        """
        Get necessary metadata to be published which will give a
        hint about the nature of data that is being published

        Args:
            document_chunk (str): A single chunk of text document
            data_entity (str): Data entity represents the source of the document chunk. It
                can be a file_url, some database table, local filepath etc

        Returns:
            StreamMetadata: Object of this class
        """
        pass

    @abstractmethod
    def read_records(self,
        config: ConnectorSpecification,
        sync_mode: str,
        cursor_field: Optional[List[str]] = None,
        stream_state: Optional[Mapping[str, Any]] = None
    ) -> DatMessage:
        pass

    @property
    def model_dict(self, ):
        return self.model_dict