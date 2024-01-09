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

    def __init__(self) -> None:
        super().__init__()

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

    def _parse_input_stream(self, input_stream: io.TextIOWrapper) -> Iterable[DatMessage]:
        """Reads from stdin, converting to Dat messages"""
        for line in input_stream:
            try:
                # import pdb;pdb.set_trace()
                _message = DatMessage.model_validate_json(line)
                print(f"message: {_message}")
                yield _message
            except ValidationError:
                logger.info(f"ignoring input which can't be deserialized as Dat Message: {line}")

    def _run_write(self, config: Mapping[str, Any], configured_catalog_path: DatCatalog) -> Iterable[DatMessage]:
        """
        Reads from stdin, converting to Dat messages, and writes to the destination.
        """
        # import pdb;pdb.set_trace()
        wrapped_stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
        catalog = DatCatalog.model_validate_json(open(configured_catalog_path).read())
        input_messages = self._parse_input_stream(wrapped_stdin)
        print(f"input_messages: {input_messages}")
        logger.info("Begin writing to the destination...")
        yield from self.write(config=config, configured_catalog=catalog, input_messages=input_messages)
        logger.info("Writing complete.")
