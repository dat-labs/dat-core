from typing import Generator, Any

class BaseSplitter:

    def __init__(self, filepath: str, strategy: str ='page', delimeter_regex: str=r'\n{1,}') -> None:
        self.filepath = filepath
        self._strategy = strategy
        self._delimeter_regex = delimeter_regex
            
    def yield_chunks(self) -> Generator[Any, Any, Any]:
        raise NotImplementedError()