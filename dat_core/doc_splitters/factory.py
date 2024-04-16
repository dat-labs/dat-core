from typing import Any, Optional
from langchain_text_splitters import (
    HTMLHeaderTextSplitter,
    HTMLSectionSplitter,
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    RecursiveJsonSplitter,
    SemanticChunker,
)
from langchain_community.document_loaders import (
    PyPDFLoader,
    OnlinePDFLoader,
    PDFMinerLoader,
    TextLoader,
)
from dat_core.doc_splitters.base_splitter import BaseSplitter

class DocumentSplitterFactory:
    """
    A factory class for creating document splitters using different loaders and splitters based on configuration keys.
    """

    def __init__(self) -> None:
        """
        Initializes a new DocumentSplitterFactory object.
        """
        self._splitters = {}
        self._loaders = {}

    def register_loader(self, key: str, loader_cls: Any) -> None:
        """
        Registers a document loader class with a specified key.

        Parameters:
            key (str): The key to identify the loader.
            loader_cls (Any): The loader class to register.
        """
        self._loaders[key] = loader_cls

    def register_splitter(self, key: str, splitter_cls: Any) -> None:
        """
        Registers a document splitter class with a specified key.

        Parameters:
            key (str): The key to identify the splitter.
            splitter_cls (Any): The splitter class to register.
        """
        self._splitters[key] = splitter_cls

    def create(self,
        filepath: str,
        loader_key: str,
        splitter_key: str,
        loader_config: Optional[dict],
        splitter_config: Optional[dict]
    ) -> BaseSplitter:
        """
        Creates a new document splitter instance based on the provided configuration.

        Parameters:
            filepath (str): The path to the document to be split.
            loader_key (str): The key corresponding to the registered loader class.
            splitter_key (str): The key corresponding to the registered splitter class.
            loader_config (Optional[dict]): Configuration parameters for the loader (optional).
            splitter_config (Optional[dict]): Configuration parameters for the splitter (optional).

        Returns:
            BaseSplitter: An instance of BaseSplitter configured with the specified loader and splitter.
        """
        _loader = self._loaders.get(loader_key)(**loader_config)
        _splitter = self._splitters.get(splitter_key)(**splitter_config)
        doc_splitter = BaseSplitter(filepath)
        doc_splitter.register_document_loader(_loader)
        doc_splitter.register_document_splitter(_splitter)
        return doc_splitter



doc_splitter_factory = DocumentSplitterFactory()

# Register doc loaders
doc_splitter_factory.register_loader('pypdf', PyPDFLoader)
doc_splitter_factory.register_loader('online_pdf', OnlinePDFLoader)
doc_splitter_factory.register_loader('pdf_miner', PDFMinerLoader)
doc_splitter_factory.register_loader('text', TextLoader)



# Register text splitters
doc_splitter_factory.register_splitter('split_by_html_header', HTMLHeaderTextSplitter)
doc_splitter_factory.register_splitter('split_by_html_section', HTMLSectionSplitter)
doc_splitter_factory.register_splitter('split_by_character', CharacterTextSplitter)
doc_splitter_factory.register_splitter('split_code', RecursiveCharacterTextSplitter)
doc_splitter_factory.register_splitter('markdown_header_text_splitter', MarkdownHeaderTextSplitter)
doc_splitter_factory.register_splitter('recursively_split_json', RecursiveJsonSplitter)
doc_splitter_factory.register_splitter('recursiverly_split_by_character', CharacterTextSplitter)
doc_splitter_factory.register_splitter('semantic_chunking', SemanticChunker)
doc_splitter_factory.register_splitter('split_by_tokens', RecursiveCharacterTextSplitter)


