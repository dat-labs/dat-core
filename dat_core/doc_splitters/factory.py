from typing import Any, Optional
from enum import Enum
from langchain_text_splitters import (
    HTMLHeaderTextSplitter,
    # HTMLSectionSplitter,
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    RecursiveJsonSplitter,
    # SemanticChunker,
)
from langchain_community.document_loaders import (
    PyPDFLoader,
    OnlinePDFLoader,
    PDFMinerLoader,
    TextLoader,
    S3FileLoader,
    UnstructuredHTMLLoader,
    UnstructuredURLLoader,
    CSVLoader,
    GoogleDriveLoader,
    WebBaseLoader,
    UnstructuredURLLoader,

)
from dat_core.doc_splitters.base_splitter import BaseSplitter


class DocLoaderType(Enum):
    PYPDF = 'PYPDF'
    ONLINE_PDF = 'ONLINE_PDF'
    PDF_MINER = 'PDF_MINER'
    TEXT = 'TEXT'
    S3 = 'S3'
    HTML = 'HTML'
    URL = 'URL'
    CSV = 'CSV'
    GOOGLE_DRIVE = 'GOOGLE_DRIVE'
    WEB_CRAWLER = 'WEB_CRAWLER'

class TextSplitterType(Enum):
    SPLIT_BY_HTML_HEADER = 'SPLIT_BY_HTML_HEADER'
    SPLIT_BY_CHARACTER = 'SPLIT_BY_CHARACTER'
    SPLIT_CODE = 'SPLIT_CODE'
    SPLIT_BY_MARKDOWN_HEADER = 'SPLIT_BY_MARKDOWN_HEADER'
    SPLIT_JSON_RECURSIVELY = 'SPLIT_JSON_RECURSIVELY'
    SPLIT_BY_CHARACTER_RECURSIVELY = 'SPLIT_BY_CHARACTER_RECURSIVELY'
    SPLIT_BY_TOKENS = 'SPLIT_BY_TOKENS'


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

    def register_loader(self, key: Enum, loader_cls: Any) -> None:
        """
        Registers a document loader class with a specified key.

        Parameters:
            key (str): The key to identify the loader.
            loader_cls (Any): The loader class to register.
        """
        self._loaders[key.value] = loader_cls

    def register_splitter(self, key: Enum, splitter_cls: Any) -> None:
        """
        Registers a document splitter class with a specified key.

        Parameters:
            key (str): The key to identify the splitter.
            splitter_cls (Any): The splitter class to register.
        """
        self._splitters[key.value] = splitter_cls

    def create(self,
        filepath: str,
        loader_key: str,
        splitter_key: str,
        loader_config: Optional[dict] = None,
        splitter_config: Optional[dict] = None
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
        if not loader_config:
            loader_config = {}
        if not splitter_config:
            splitter_config = {}
        _loader = self._loaders.get(loader_key)(**loader_config)
        _splitter = self._splitters.get(splitter_key)(**splitter_config)
        doc_splitter = BaseSplitter(filepath)
        doc_splitter.register_document_loader(_loader)
        doc_splitter.register_document_splitter(_splitter)
        return doc_splitter



doc_splitter_factory = DocumentSplitterFactory()

# Register doc loaders
doc_splitter_factory.register_loader(DocLoaderType.PYPDF, PyPDFLoader)
doc_splitter_factory.register_loader(DocLoaderType.ONLINE_PDF, OnlinePDFLoader)
doc_splitter_factory.register_loader(DocLoaderType.PDF_MINER, PDFMinerLoader)
doc_splitter_factory.register_loader(DocLoaderType.TEXT, TextLoader)
doc_splitter_factory.register_loader(DocLoaderType.S3, S3FileLoader)
doc_splitter_factory.register_loader(DocLoaderType.HTML, UnstructuredHTMLLoader)
doc_splitter_factory.register_loader(DocLoaderType.URL, UnstructuredURLLoader)
doc_splitter_factory.register_loader(DocLoaderType.CSV, CSVLoader)
doc_splitter_factory.register_loader(DocLoaderType.GOOGLE_DRIVE, GoogleDriveLoader)
doc_splitter_factory.register_loader(DocLoaderType.WEB_CRAWLER, WebBaseLoader)



# Register text splitters
doc_splitter_factory.register_splitter(TextSplitterType.SPLIT_BY_HTML_HEADER, HTMLHeaderTextSplitter)
# doc_splitter_factory.register_splitter('split_by_html_section', HTMLSectionSplitter)
doc_splitter_factory.register_splitter(TextSplitterType.SPLIT_BY_CHARACTER, CharacterTextSplitter)
doc_splitter_factory.register_splitter(TextSplitterType.SPLIT_CODE, RecursiveCharacterTextSplitter)
doc_splitter_factory.register_splitter(TextSplitterType.SPLIT_BY_MARKDOWN_HEADER, MarkdownHeaderTextSplitter)
doc_splitter_factory.register_splitter(TextSplitterType.SPLIT_JSON_RECURSIVELY, RecursiveJsonSplitter)
doc_splitter_factory.register_splitter(TextSplitterType.SPLIT_BY_CHARACTER_RECURSIVELY, RecursiveCharacterTextSplitter)
# doc_splitter_factory.register_splitter('semantic_chunking', SemanticChunker)
doc_splitter_factory.register_splitter(TextSplitterType.SPLIT_BY_TOKENS, RecursiveCharacterTextSplitter)


