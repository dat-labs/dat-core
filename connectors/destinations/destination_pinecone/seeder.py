import uuid
import itertools
import pinecone
from typing import Any, List, Optional, Tuple, Iterator, Iterable, Dict
from connectors.destinations.vector_db_helpers.seeder import Seeder, Chunk
from connectors.destinations.vector_db_helpers.utils import create_chunks

PINECONE_BATCH_SIZE = 40

PARALLELISM_LIMIT = 4

MAX_METADATA_SIZE = 40960 - 10000

MAX_IDS_PER_DELETE = 1000

class PineconeSeeder(Seeder):
    def __init__(self, config: Any, embedding_dimensions: int):
        super().__init__(config)
        pinecone.init(api_key=config.connectionSpecification.get('pinecone_api_key'), environment=config.connectionSpecification.get('pinecone_environment'))
        self.pinecone_index = pinecone.Index(config.connectionSpecification.get('pinecone_index'))
        self.embedding_dimensions = embedding_dimensions

    def seed(self, document_chunks: List[Chunk], namespace: str, stream: str) -> None:
        pinecone_docs = []
        for document_chunk in document_chunks:
            chunk = document_chunk
            metadata = chunk.metadata
            metadata["text"] = chunk.page_content
            pinecone_docs.append((str(uuid.uuid4()), chunk.embedding, metadata))
        serial_batches = create_chunks(pinecone_docs, batch_size=PINECONE_BATCH_SIZE * PARALLELISM_LIMIT)
        for batch in serial_batches:
            async_results = [
                self.pinecone_index.upsert(vectors=ids_vectors_chunk, async_req=True, show_progress=False, namespace=namespace)
                for ids_vectors_chunk in create_chunks(batch, batch_size=PINECONE_BATCH_SIZE)
            ]
            [async_result.get() for async_result in async_results]

    def delete(self, filter, namespace=None):
        _pod_type = pinecone.describe_index(self.config.connectionSpecification.get('pinecone_index')).pod_type
        if _pod_type == "starter":
            # Starter pod types have a maximum of 100000 rows
            top_k = 10000
            self.delete_by_metadata(filter, top_k, namespace)
        else:
            self.pinecone_index.delete(filter=filter, namespace=namespace)

    def delete_by_metadata(self, filter, top_k, namespace=None):
        zero_vector = [0.0] * self.embedding_dimensions
        query_result = self.pinecone_index.query(
            vector=zero_vector, filter=filter, top_k=top_k, namespace=namespace)
        while len(query_result.matches) > 0:
            vector_ids = [doc.id for doc in query_result.matches]
            if len(vector_ids) > 0:
                # split into chunks of 1000 ids to avoid id limit
                batches = create_chunks(vector_ids, batch_size=MAX_IDS_PER_DELETE)
                for batch in batches:
                    self.pinecone_index.delete(ids=list(batch), namespace=namespace)
            query_result = self.pinecone_index.query(
                vector=zero_vector, filter=filter, top_k=top_k, namespace=namespace)

    def check(self) -> Optional[str]:
        try:
            indexes = pinecone.list_indexes()
            index = self.config.connectionSpecification.get('pinecone_index')
            if index not in indexes:
                return False, f"Index {index} does not exist in environment {self.config.connectionSpecification.get('pinecone_environment')}."
            description = pinecone.describe_index(index)
            if description.dimension != self.embedding_dimensions:
                return (False,
                        (f"Index {index} has dimension {description.dimension} "
                         f"but configured dimension is {self.embedding_dimensions}."))
        except Exception as e:
            raise e
        return True, description
