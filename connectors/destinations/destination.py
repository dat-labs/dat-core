import io
import sys
from abc import ABC, abstractmethod
from loguru import logger
from typing import Any, Iterable, List, Mapping
from pydantic import ValidationError
from pydantic_models.dat_message import DatMessage
from pydantic_models.dat_catalog import DatCatalog
from connectors.base import ConnectorBase


class Destination(ConnectorBase):
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
            configured_catalog (ConfiguredDatCatalog): Catalog describing the configured schema for the destination.
            input_messages (Iterable[DatMessage]): Iterable of messages containing data to be written to the destination.

        Returns:
            Iterable[DatMessage]: Iterable of messages representing the written data.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
