# generated by datamodel-codegen:
#   filename:  DatMessage.yml
#   timestamp: 2024-02-12T14:56:37+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import AnyUrl, BaseModel, Extra, Field
from pydantic_models.dat_catalog import DatCatalog
from pydantic_models.dat_log_message import DatLogMessage
from pydantic_models.stream_metadata import StreamMetadata
from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_document_stream import DatDocumentStream

class Type(Enum):
    RECORD = 'RECORD'
    STATE = 'STATE'
    LOG = 'LOG'
    SPEC = 'SPEC'
    CONNECTION_STATUS = 'CONNECTION_STATUS'
    CATALOG = 'CATALOG'
    TRACE = 'TRACE'

class Status(Enum):
    SUCCEEDED = 'SUCCEEDED'
    FAILED = 'FAILED'


class DatConnectionStatus(BaseModel):
    class Config:
        extra = 'allow'

    status: Status
    message: Optional[str] = None



class StreamStatus(Enum):
    STARTED = 'STARTED'


class StreamState(BaseModel):
    class Config:
        extra = 'allow'

    data: Dict[str, Any] = Field(..., description='the state data')
    stream_status: Optional[StreamStatus] = Field(None, description='the stream status')


class DatStateMessage(BaseModel):
    class Config:
        extra = 'allow'

    stream: Optional[DatDocumentStream] = None
    stream_state: Optional[StreamState] = None




class Data(BaseModel):
    document_chunk: Optional[str] = Field(
        None, description='document chunks emitted by source'
    )
    vectors: Optional[List[float]] = Field(
        None, description='vectors generated by a Generator'
    )
    metadata: Optional[StreamMetadata] = Field(
        None,
        description='metadata generated by a Source, to be passed through Generator and loaded to Destination',
    )


class DatDocumentMessage(BaseModel):
    class Config:
        extra = 'allow'

    namespace: Optional[str] = Field(
        None, description='namespace the data is associated with'
    )
    stream: DatDocumentStream = Field(
        None, description='stream the data is associated with'
    )
    data: Data = Field(..., description='record data')
    emitted_at: int = Field(
        ...,
        description='when the data was emitted from the source. epoch in millisecond.',
    )


class DatMessage(BaseModel):
    class Config:
        extra = 'allow'

    type: Type = Field(..., description='Message type')
    log: Optional[DatLogMessage] = Field(
        None,
        description='log message: any kind of logging you want the platform to know about.',
    )
    spec: Optional[ConnectorSpecification] = None
    connectionStatus: Optional[DatConnectionStatus] = None
    catalog: Optional[DatCatalog] = Field(
        None, description='catalog message: the catalog'
    )
    record: Optional[DatDocumentMessage] = Field(
        None, description='record message: the record'
    )
    state: Optional[DatStateMessage] = Field(
        None,
        description='schema message: the state. Must be the last message produced. The platform uses this information',
    )
