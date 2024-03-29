import re
from typing import Generator, Any
from dat_core.doc_splitters.base_splitter import BaseSplitter

class TxtSplitter(BaseSplitter):

    def yield_chunks(self) -> Generator[Any, Any, Any]:
        with open(self.filepath, 'r') as _f:
            for chunk in re.split(self._delimeter_regex, _f.read()):
                if chunk.strip():
                    yield chunk