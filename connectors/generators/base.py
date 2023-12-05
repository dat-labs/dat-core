#! /Users/rijumone/Kitchen/dat-core/.venv/bin/python
# import click
# from abc import abstractmethod
from connectors.base import ConnectorBase
import openai
from langchain.embeddings.openai import OpenAIEmbeddings


class GeneratorBase(ConnectorBase):
    """Base abstract class for generators.
    """

    def __init__(self) -> None:
        super().__init__()

    
import os
from typing import Any, Mapping, Tuple
class OpenAI(GeneratorBase):
    _spec_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'specs.yml')

    def check_connection(self, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            _r = OpenAIEmbeddings(
                openai_api_key=os.getenv('OPENAI_API_KEY', None),
            ).embed_query('foo')
        except openai.AuthenticationError:
            raise
        return (True, _r)
    

if __name__ == '__main__':
    s = OpenAI().spec()
    print(s)

    c = OpenAI().check(config='generator_config.json')
    print(c)