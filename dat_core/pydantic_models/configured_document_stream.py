# generated by datamodel-codegen:
#   filename:  ConfiguredDocumentStream.yml
#   timestamp: 2024-02-13T11:14:27+00:00

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field
from dat_core.pydantic_models.dat_document_stream import DatDocumentStream, ReadSyncMode
from dat_core.pydantic_models.base import EnumWithStr


class DestinationSyncMode(EnumWithStr):
    UPSERT = 'upsert'
    APPEND = 'append'
    REPLACE = 'replace'


class ConfiguredDocumentStream(BaseModel):
    class Config:
        extra = 'allow'

    stream: DatDocumentStream
    read_sync_mode: ReadSyncMode
    write_sync_mode: DestinationSyncMode
    cursor_field: Optional[List[str]] = Field(
        None,
        description='Path to the field that will be used to determine if a record is new or modified since the last sync. This field is REQUIRED if `read_sync_mode` is `incremental`. Otherwise it is ignored.',
    )
    primary_key: Optional[List[List[str]]] = Field(
        None,
        description='Paths to the fields that will be used as primary key. This field is REQUIRED if `write_sync_mode` is `*_dedup`. Otherwise it is ignored.',
    )
