from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import AnyUrl, BaseModel, Field

class DestinationSyncMode(Enum):
    append = 'append'
    replace = 'replace'
    upsert = 'upsert'


class ConnectorSpecification(BaseModel):
    class Config:
        extra = 'allow'

    protocol_version: Optional[str] = Field(
        None,
        description='the Vectorize Protocol version supported by the connector. Protocol versioning uses SemVer.',
    )
    documentationUrl: Optional[AnyUrl] = None
    changelogUrl: Optional[AnyUrl] = None
    connectionSpecification: Dict[str, Any] = Field(
        ...,
        description='ConnectorDefinition specific blob. Must be a valid JSON string.',
    )
    supportsIncremental: Optional[bool] = Field(
        None, description='If the connector supports incremental mode or not.'
    )
    supported_destination_sync_modes: Optional[List[DestinationSyncMode]] = Field(
        None, description='List of destination sync modes supported by the connector'
    )
