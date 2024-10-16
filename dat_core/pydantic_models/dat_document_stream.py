# generated by datamodel-codegen:
#   filename:  DatDocumentStream.yml
#   timestamp: 2024-05-27T08:47:49+00:00

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field
from dat_core.pydantic_models.base import EnumWithStr


class ReadSyncMode(EnumWithStr):
    FULL_REFRESH = 'FULL_REFRESH'
    INCREMENTAL = 'INCREMENTAL'


class WriteSyncMode(EnumWithStr):
    APPEND = 'APPEND'
    UPSERT = 'UPSERT'
    REPLACE = 'REPLACE'

class BaseSplitterSettings(BaseModel):
    def get_splitter_config(self, splitter_settings: Dict[str, Any]) -> Dict[str, Any]:
        splitter_config = {}
        for key, value in splitter_settings.items():
            if key != 'splitter_settings':
                splitter_config[key] = value
        return splitter_config

class SplitByHtmlHeaderExtraConfig(BaseSplitterSettings):
    headers_to_split_on: Optional[List[str]] = Field(
        ['h2', 'h3'],
        description='list of headers we want to track mapped to (arbitrary) keys for metadata. Allowed header values: h1, h2, h3, h4, h5, h6',
        json_schema_extra={
            'ui-opts': {
                'widget': 'textboxDelimiterSeparatedChip',
            }
        }
    )


class SplitByHtmlHeaderSettings(BaseSplitterSettings):
    splitter_settings: Optional[str] = Field('SPLIT_BY_HTML_HEADER', json_schema_extra={
        'ui-opts': {
            'hidden': True,
        }
    })
    headers_to_split_on: Optional[List[str]] = Field(
        ['h2', 'h3'],
        description='list of headers we want to track mapped to (arbitrary) keys for metadata. Allowed header values: h1, h2, h3, h4, h5, h6',
        json_schema_extra={
            'ui-opts': {
                'widget': 'textboxDelimiterSeparatedChip',
            }
        }
    )

    class Config:
        extra = 'allow' 


class SplitByCharacterSettings(BaseSplitterSettings):
    splitter_settings: Optional[str] = Field(
        'SPLIT_BY_CHARACTER',
        json_schema_extra={
            'ui-opts': {
                'hidden': True,
            }
        }
    )
    separator: Optional[str] = '\\n\\n'


class SplitCodeSettings(BaseSplitterSettings):
    splitter_settings: Optional[str] = Field(
        'SPLIT_CODE',
        json_schema_extra={
            'ui-opts': {
                'hidden': True,
            }
        }
    )
    separators: Optional[List] = Field(
        ['\\nclass ', '\\ndef '],
        json_schema_extra={
            'ui-opts': {
                'widget': 'textboxDelimiterSeparatedChip',
            }
        }
    )


class SplitByMarkdownSettings(BaseSplitterSettings):
    splitter_settings: Optional[str] = Field(
        'SPLIT_BY_MARKDOWN',
        json_schema_extra={
            'ui-opts': {
                'hidden': True,
            }
        }
    )


class SplitJsonRecursivelySettings(BaseSplitterSettings):
    splitter_settings: Optional[str] = Field(
        'SPLIT_JSON_RECURSIVELY',
        json_schema_extra={
            'ui-opts': {
                'hidden': True,
            }
        }
    )


class SplitByCharacterRecursiverlySettings(BaseSplitterSettings):
    splitter_settings: Optional[str] = Field(
        'SPLIT_BY_CHARACTER_RECURSIVELY',
        json_schema_extra={
            'ui-opts': {
                'hidden': True,
            }
        }
    )
    separators: Optional[List] = ['\n\n', '\n', ' ', '']


class SplitByTokensSettings(BaseSplitterSettings):
    splitter_settings: Optional[str] = Field(
        'SPLIT_BY_TOKENS',
        json_schema_extra={
            'ui-opts': {
                'hidden': True,
            }
        }
    )
    separators: Optional[List] = ['\n\n', '\n', ' ', '']


class Advanced(BaseModel):
    splitter_settings: Optional[
        Union[
            SplitByHtmlHeaderSettings,
            SplitByCharacterSettings,
            SplitCodeSettings,
            SplitByMarkdownSettings,
            SplitJsonRecursivelySettings,
            SplitByCharacterRecursiverlySettings,
            SplitByTokensSettings,
        ]
    ] = Field(
        None,
        description='Splitter settings.',
        json_schema_extra={
            'ui-opts': {
                'widget': 'singleDropdown',
            }
        }
    )


class DatDocumentStream(BaseModel):
    class Config:
        extra = 'allow'

    name: str = Field(
        ...,
        description='The name of the document stream.',
        title='Name',
        json_schema_extra={
            'ui-opts': {
                'hidden': True,
            }
        }
    )
    json_schema: Optional[Dict[str, Any]] = Field(
        None,
        description='Stream schema using Json schema specification.',
        title='Json Schema',
        json_schema_extra={
            'ui-opts': {
                'hidden': True,
            }
        }
    )
    namespace: Optional[str] = Field(
        None, description='The namespace the data is associated with.',
        title='Namespace',
    )
    read_sync_mode: Optional[ReadSyncMode] = Field(
        ReadSyncMode.FULL_REFRESH.name,
        description='An list of supported sync modes for the stream while reading.',
        title='Read Sync Mode',
        json_schema_extra={
            'ui-opts': {
                'widget': 'radioButton',
            }
        }
    )
    write_sync_mode: Optional[WriteSyncMode] = Field(
        WriteSyncMode.APPEND.name,
        description='A list of supported sync modes for the stream while writing.',
        title='Write Sync Mode',
        json_schema_extra={
            'ui-opts': {
                'widget': 'radioButton',
            }
        }
    )
    # Keeping this field optional and hidden because either source will have a default 
    # (developer decided) cursor value or it will be set by the user by selecting the stream field in the UI
    cursor_field: Optional[str] = Field(
        None,
        description='The path to the field used to determine if a record is new or modified.\nREQUIRED for INCREMENTAL sync mode.',
        title='Cursor Field',
        json_schema_extra={
            'ui-opts': {
                'hidden': True,
            }
        }
    )
    upsert_keys: Optional[List[str]] = Field(
        None,
        description='The keys to use for upserting records.',
        title='Upsert Keys',
        json_schema_extra={
            'ui-opts': {
                'hidden': True,
            }
        }
    )
    advanced: Optional[Advanced] = Field(
        None,
        description='Additional Settings',
        title='Advanced Settings',
        json_schema_extra={
            'ui-opts': {
                'widget': 'group',
                'collapsible': True,
            }
        }
    )

