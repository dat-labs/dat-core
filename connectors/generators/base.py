from typing import Any, Tuple
import os
from typing import Iterator
from abc import abstractmethod
from connectors.base import ConnectorBase
from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_message import DatMessage, Type


class GeneratorBase(ConnectorBase):
    """Base abstract class for generators.
    """

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def generate(
        self,
        config: ConnectorSpecification,
        dat_message: DatMessage
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


import openai
from langchain.embeddings.openai import OpenAIEmbeddings
class OpenAI(GeneratorBase):
    _spec_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'specs/openai-specs.yml')

    def check_connection(self, config: ConnectorSpecification) -> Tuple[bool, Any]:
        try:
            _r = OpenAIEmbeddings(
                openai_api_key=config.connectionSpecification.get(
                    'openai_api_key'),
            ).embed_query('foo')
        except openai.AuthenticationError:
            raise
        return (True, _r)
    
    def generate(
        self,
        config: ConnectorSpecification,
        dat_message: DatMessage
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

        dat_message.record.data.vectors = OpenAIEmbeddings(
            openai_api_key=config.connectionSpecification.get(
                'openai_api_key'),
        ).embed_query(dat_message.record.data.document_chunk)
        yield dat_message


from sentence_transformers import SentenceTransformer
class SentenceTransformers(GeneratorBase):
    _spec_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'specs/sentencetransformers-specs.yml')
    
    def check_connection(self, config: ConnectorSpecification) -> Tuple[bool, Any]:
        return (True, None)

    def generate(
        self,
        config: ConnectorSpecification,
        dat_message: DatMessage
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
        
        dat_message.record.data.vectors = SentenceTransformer('all-MiniLM-L6-v2').encode(
            dat_message.record.data.document_chunk)
        yield dat_message

if __name__ == '__main__':
    from pydantic_models.dat_message import DatDocumentMessage, Data
    # s = OpenAI().spec()
    # print(s)

    # c = OpenAI().check(config=ConnectorSpecification.model_validate_json(
    #         open('generator_config.json').read()),)
    # print(c)

    # e = OpenAI().generate(
    #     config=ConnectorSpecification.model_validate_json(
    #         open('generator_config.json').read()),
    #     dat_message=DatMessage(
    #         type=Type.RECORD,
    #         record=DatDocumentMessage(
    #             data=Data(
    #                 document_chunk='foo',
    #             ),
    #             emitted_at=1,
    #         ),
    #     )
    # )
    # print(list(e))

    # s = SentenceTransformers().spec()
    # print(s)

    # c = SentenceTransformers().check(
    #     config=ConnectorSpecification.model_validate(
    #         {'connectionSpecification': {}}),)
    # print(c)
    
    e = SentenceTransformers().generate(
        config=ConnectorSpecification.model_validate_json(
            open('generator_config.json').read()),
        dat_message=DatMessage(
            type=Type.RECORD,
            record=DatDocumentMessage(
                data=Data(
                    document_chunk='foo',
                ),
                emitted_at=1,
            ),
        )
    )
    print(list(e))