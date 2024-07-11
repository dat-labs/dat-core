"""
Module: base_splitter_module

This module contains the definition of the BaseSplitter class, which is used for document splitting.

Classes:
    BaseSplitter: A class for document splitting operations.

Dependencies:
    - typing: Used for type hints.
    - langchain_text_splitters.TextSplitter: A text splitter class from the langchain_text_splitters module.
    - dat_core.doc_splitters.Document: A document class from the dat_core.doc_splitters module.
    - langchain_text_splitters.RecursiveCharacterTextSplitter: A recursive character text splitter class from langchain_text_splitters module.
    - langchain_community.document_loaders.base.BaseLoader: A base document loader class from the langchain_community.document_loaders.base module.
"""

from typing import Generator, Any, Optional
from dat_core.doc_splitters import Document

class BaseSplitter:
    """
    BaseSplitter class for document splitting operations.

    Attributes:
        _default_splitter (Any): The default splitter object.
        _default_loader (Any): The default loader object.

    Methods:
        register_document_loader: Registers a document loader object.
        register_document_splitter: Registers a document splitter object.
        load: Loads documents using the registered loader.
        load_and_chunk: Loads and chunks documents using the registered loader and splitter.
        split_text: Splits text using the registered splitter.
    """

    def __init__(self) -> None:
        """
        Initializes a new BaseSplitter object.
        """
        self._default_splitter = None
        self._default_loader = None
    
    def register_document_loader(self, loader_object: Any) -> None:
        """
        Registers a document loader object.

        Parameters:
            loader_object (Any): The document loader object to register.
        """
        self._default_loader = loader_object
    
    def register_document_splitter(self, splitter_object: Any) -> None:
        """
        Registers a document splitter object.

        Parameters:
            splitter_object (Any): The document splitter object to register.
        """
        self._default_splitter = splitter_object
    
    def load(self, **kwargs) -> Generator[Document, Any, Any]:
        """
        Loads documents using the registered loader.

        Yields:
            Generator[Document, Any, Any]: A generator yielding Document objects.
        """
        if not self._default_loader:
            raise Exception('Please register a document loader first using register_document_loader()')
        
        try:
            docs = self._default_loader.lazy_load(**kwargs) # langchain loaders lazy_load
        except NotImplementedError:
            docs = self._default_loader.load(**kwargs) # langchain loaders default load
        except AttributeError:
            try:
                docs = self._default_loader.lazy_load_data(**kwargs) # llama index loaders lazy_load
            except NotImplementedError:
                docs = self._default_loader.load_data(**kwargs) # llama index default load method
            
        
        for doc in docs:
            try:
                yield Document.from_langchain_document(doc)
            except (AttributeError, KeyError):
                yield Document.from_llama_index_document(doc)

    def load_and_chunk(self, **kwargs) -> Generator[Document, Any, Any]:
        """
        Loads and chunks documents using the registered loader and splitter.

        Parameters:
            doc_loader (Optional[Any]): An optional document loader object.
            text_splitter (Optional[Any]): An optional text splitter object.

        Yields:
            Generator[Document, Any, Any]: A generator yielding chunks of Document.
        """
        if not self._default_loader:
            raise Exception('Please register a document loader first using register_document_loader()')
        if not self._default_splitter:
            raise Exception('Please register a document splitter first using register_document_splitter()')

        docs = self.load(**kwargs)

        for doc in docs:
            yield from self.split_text(doc.page_content)
    
    def split_text(self, text: str) -> Generator[str, Any, Any]:
        """
        Splits text using the registered splitter.

        Parameters:
            text (str): The text to be split.

        Yields:
            Generator[str, Any, Any]: A generator yielding split text fragments.
        """
        for txt in self._default_splitter.split_text(text):
            yield txt
