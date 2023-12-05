from typing import Dict, List, Optional, Iterable, Mapping, Any
from abc import ABC, abstractmethod
from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_catalog import DocumentStream, SyncMode

class Stream(ABC):
    """
    Base abstract class for a Dat Stream
    """
    def __init__(self, config: ConnectorSpecification) -> None:
        self.config = config

    @property
    def name(self) -> str:
        """
        Returns the name of the stream. Ideally it should be a
        camel case string matching the class name.
        """
        # TODO: Make a function for camel case
        return self.__class__.__name__
    
    @property
    def sync_mode(self) -> SyncMode:
        # TODO: Fix return
        return SyncMode.incremental
    
    def as_pydantic_model(self) -> DocumentStream:
        return DocumentStream(name=self.name, sync_mode=self.sync_mode)

    @abstractmethod
    def read_records(self,
        config: ConnectorSpecification,
        sync_mode: str,
        cursor_field: Optional[List[str]] = None,
        stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Dict]:
        pass