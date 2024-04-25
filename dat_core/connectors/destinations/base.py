from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping
from dat_core.connectors.base import ConnectorBase
from dat_core.pydantic_models import (
    DatMessage, DatCatalog
)


class DestinationBase(ConnectorBase):
    """
    Abstract base class for defining a destination connector.

    Subclasses must implement the `write` method to define how the connector writes data to the destination.

    Attributes:
        None
    """

    @abstractmethod
    def write(
        self, config: Mapping[str, Any], configured_catalog: DatCatalog, input_messages: Iterable[DatMessage]
    ) -> Iterable[DatMessage]:
        """
        Abstract method to be implemented by subclasses.

        Args:
            config (Mapping[str, Any]): Configuration parameters for the destination.
            configured_catalog (DatCatalog): Catalog describing the configured schema for the destination.
            input_messages (Iterable[DatMessage]): Iterable of messages containing data to be written to the destination.

        Returns:
            Iterable[DatMessage]: Iterable of messages representing the written data.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
