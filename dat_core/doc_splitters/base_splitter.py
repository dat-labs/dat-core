from typing import Generator, Any

class BaseSplitter:
    """
    Base class for splitting files into chunks based on a specified strategy.

    Args:
        filepath (str): The path to the file to be split.
        strategy (str, optional): The splitting strategy. Defaults to 'page'.
        delimeter_regex (str, optional): The regex pattern used as the delimiter for splitting. Defaults to r'\n{1,}'.

    Attributes:
        filepath (str): The path to the file being split.
        _strategy (str): The splitting strategy.
        _delimeter_regex (str): The regex pattern used as the delimiter for splitting.

    Methods:
        yield_chunks(self) -> Generator[Any, Any, Any]: Abstract method to yield chunks of data from the file.
    """

    def __init__(self, filepath: str, strategy: str = 'page', delimeter_regex: str = r'\n{1,}') -> None:
        """
        Initialize the BaseSplitter instance.

        Args:
            filepath (str): The path to the file to be split.
            strategy (str, optional): The splitting strategy. Defaults to 'page'.
            delimeter_regex (str, optional): The regex pattern used as the delimiter for splitting. Defaults to r'\n{1,}'.
        """
        self.filepath = filepath
        self._strategy = strategy
        self._delimeter_regex = delimeter_regex
            
    def yield_chunks(self) -> Generator[Any, Any, Any]:
        """
        Abstract method to yield chunks of data from the file.

        Raises:
            NotImplementedError: This method must be implemented in subclasses.
        """
        raise NotImplementedError()
