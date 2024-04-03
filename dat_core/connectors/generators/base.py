from typing import Any, Tuple
import os
from typing import Iterator
from abc import abstractmethod
from dat_core.connectors.base import ConnectorBase
from dat_core.pydantic_models import (
    ConnectorSpecification,
    DatMessage,
)


class GeneratorBase(ConnectorBase):
    """Base abstract class for generators.
    """

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def generate(
        self,
        config: ConnectorSpecification,
        dat_message: DatMessage
    ) -> Iterator[DatMessage]:
        """
        The generator operation will generator vector chunks

        Args:
            config (ConnectorSpecification): The user-provided configuration as specified by
              the generator's spec.
            document_chunks: DatMessage containing 
        Yields:
            Iterator[Dict]: Each row should be wrapped around a DatMessage obj
        """

