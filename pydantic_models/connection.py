from __future__ import annotations
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_models.connector_specification import ConnectorSpecification


class Spec(BaseModel):
    source: ConnectorSpecification
    generator: ConnectorSpecification
    destination: ConnectorSpecification


class Connection(BaseModel):
    class Config:
        extra = 'allow'

    protocol_version: Optional[str] = Field(
        None,
        description='the Vectorize Protocol version supported by the connector. Protocol versioning uses SemVer.',
    )
    spec: Spec = Field(
        ...,
        description='ConnectorDefinition specific blob. Must be a valid JSON string.',
    )
