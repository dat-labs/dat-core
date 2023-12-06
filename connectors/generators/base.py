#! /Users/rijumone/Kitchen/dat-core/.venv/bin/python
# import click
import json
from typing import Iterator, List
import openai
from langchain.embeddings.openai import OpenAIEmbeddings
from utils import schema_validate
from connectors.base import ConnectorBase
from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_message import DatMessage, Type


class GeneratorBase(ConnectorBase):
    """Base abstract class for generators.
    """

    def __init__(self) -> None:
        super().__init__()

    def generate(
        self,
        config: ConnectorSpecification,
        document_chunk: DatMessage
    ) -> Iterator[DatMessage]:
        """
        The generator operation will generator vector chunks

        Args:
            config (ConnectorSpecification): The user-provided configuration as specified by
              the generator's spec.
            document_chunks: DatMessage containing 
        Yields:
            Iterator[Dict]: Each row should be wrapped around a DatMessage obj
        """
        
        _r = OpenAIEmbeddings(
            openai_api_key=config.connectionSpecification.get('openai_api_key'),
        ).embed_query(document_chunk.record.data.document_chunk)
        print(_r)


    

    
import os
from typing import Any, Mapping, Tuple
from pydantic_models.dat_message import DatDocumentMessage, Data
class OpenAI(GeneratorBase):
    _spec_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'specs.yml')

    def check_connection(self, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            _r = OpenAIEmbeddings(
                openai_api_key=config.connectionSpecification.get('openai_api_key'),
            ).embed_query('foo')
        except openai.AuthenticationError:
            raise
        return (True, _r)
    

if __name__ == '__main__':
    # s = OpenAI().spec()
    # print(s)

    # c = OpenAI().check(config=ConnectorSpecification.model_validate_json(
    #         open('generator_config.json').read()),)
    # print(c)
    
    e = OpenAI().generate(
        config=ConnectorSpecification.model_validate_json(
            open('generator_config.json').read()),
        document_chunk=DatMessage(
            type=Type.RECORD,
            record=DatDocumentMessage(
                data=Data(
                    document_chunk='foo',
                    ),
                emitted_at=1,
            ),
        )    
    )
    print(e)