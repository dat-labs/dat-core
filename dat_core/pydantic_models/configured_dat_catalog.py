from typing import List
from pydantic import BaseModel
from dat_core.pydantic_models.configured_document_stream import ConfiguredDocumentStream

class ConfiguredDatCatalog(BaseModel):
    document_streams: List[ConfiguredDocumentStream]
