from typing import Dict, List, Optional, Iterable, Mapping, Any
from abc import ABC, abstractmethod
from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_catalog import DocumentStream, SyncMode
from utils import to_snake_case

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
        return SyncMode.incremental
    
    @property
    def json_schema(self) -> Mapping[str, Any]:
        return self._schema
    
    def as_pydantic_model(self) -> DocumentStream:
        return DocumentStream(name=self.name, sync_mode=self.sync_mode, json_schema=self.json_schema)
    
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
    def read_records(self,
        config: ConnectorSpecification,
        sync_mode: str,
        cursor_field: Optional[List[str]] = None,
        stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Dict]:
        pass