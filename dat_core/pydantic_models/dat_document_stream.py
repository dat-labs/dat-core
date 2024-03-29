# generated by datamodel-codegen:
#   filename:  DatDocumentStream.yml
#   timestamp: 2024-03-19T12:20:43+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from dat_core.pydantic_models.base import EnumWithStr


class SyncMode(EnumWithStr):
    full_refresh = 'full_refresh'
    incremental = 'incremental'


class DatDocumentStream(BaseModel):
    class Config:
        extra = 'allow'

    name: str
    namespace: Optional[str] = Field(
        None, description='namespace the data is associated with'
    )
    json_schema: Optional[Dict[str, Any]] = None
    dir_uris: Optional[List[str]] = None
    supported_sync_modes: List[SyncMode] = Field(
        ..., description='List of sync modes supported by this stream.', min_items=1
    )
    default_cursor_field: Optional[str] = Field(
        None,
        description='default cursor field to use for incremental syncs',
    )
