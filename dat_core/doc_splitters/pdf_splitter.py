import re
from typing import Generator, Any
from pypdf import PdfReader
from dat_core.doc_splitters.base_splitter import BaseSplitter

class PdfSplitter(BaseSplitter):
    
    def yield_chunks_by_paragraph(self) -> Generator[Any, Any, Any]:
        for page_content in self.yield_chunks_by_page():
            for chunk in re.split(self._delimeter_regex, page_content):
                if chunk.strip():
                    yield chunk
    
    def yield_chunks_by_page(self) -> Generator[Any, Any, Any]:
        reader = PdfReader(self.filepath)
        for page in reader.pages:
            yield page.extract_text()
    
    def yield_chunks(self) -> Generator[Any, Any, Any]:
        if self._strategy == 'paragraph':
            for chunk in self.yield_chunks_by_paragraph():
                yield chunk
        else:
            for chunk in self.yield_chunks_by_page():
                yield chunk