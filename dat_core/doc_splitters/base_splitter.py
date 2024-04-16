from typing import Generator, Any, List, Optional, Iterator
from langchain_text_splitters import TextSplitter
from dat_core.doc_splitters import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.base import BaseLoader

class BaseSplitter:

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self._default_splitter = None
        self._default_loader = None
    
    def register_document_loader(self, loader_object: Any) -> None:
        self._default_loader = loader_object
    
    def register_document_splitter(self, splitter_object: Any) -> None:
        self._default_splitter = splitter_object
    
    def load(self) -> Generator[Document, Any, Any]:
        if not self._default_loader:
            raise Exception('Please register a document loader first using register_document_loader()')
        
        for doc in self._default_loader.load():
            yield doc


    def load_and_chunk(self, doc_loader: Optional[Any] = None, text_splitter: Optional[Any] = None) -> Generator[str, Any, Any]:
        if not self._default_loader:
            raise Exception('Please register a document loader first using register_document_loader()')
        if not self._default_splitter:
            raise Exception('Please register a document splitter first using register_document_splitter()')

        docs = self.load()

        for doc in self._default_splitter.split_documents(docs):
            yield from self._default_splitter.split_text(doc.page_content)
    
    def split_text(self, text: str) -> Generator[str, Any, Any]:
        for txt in self._default_splitter.split_text(text):
            yield txt
