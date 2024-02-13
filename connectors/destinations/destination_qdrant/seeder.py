import uuid
from qdrant_client import QdrantClient
from typing import Any, List, Optional
from connectors.destinations.vector_db_helpers.seeder import Seeder, Chunk
from connectors.destinations.vector_db_helpers.utils import create_chunks
from qdrant_openapi_client.models import VectorParams, Distance


DISTANCE_METRIC_MAP = {
    "dot": Distance.DOT,
    "cos": Distance.COSINE,
    "euc": Distance.EUCLID,
}

class QdrantSeeder(Seeder):
    def __init__(self, config: Any, embedding_dimensions: int):
        super().__init__(config)
        self.embedding_dimensions = embedding_dimensions

    def seed(self, document_chunks: List[Chunk], namespace: str, stream: str) -> None:
        pass
        # for chunk in document_chunks:
        #     metadata = chunk.metadata
        #     metadata["text"] = chunk.page_content
        #     self.qdrant_client.upsert(
        #         index_name=namespace,
        #         data=[{
        #             "id": str(uuid.uuid4()),
        #             "vector": chunk.embedding,
        #             "metadata": metadata
        #         }]
        #     )

    def delete(self, filter, namespace=None):
        pass
        # self.qdrant_client.delete(index_name=namespace, filter=filter)

    def check(self) -> Optional[str]:
        try:
            self._create_client()

            if not self._client:
                return (False, "Qdrant is not alive")
            available_collections = [collection.name for collection in self._client.get_collections().collections]
            distance = DISTANCE_METRIC_MAP.get(self.config.connectionSpecification.get('distance'))
            collection_name = self.config.connectionSpecification.get('collection')
            if collection_name in available_collections:
                description = self._client.get_collection(collection_name=collection_name)
                if description.config.params.vectors.size != self.embedding_dimensions:
                    return (False,
                            f"Collection {collection_name} has dimension {description.config.params.size}, "
                            f"but the configured dimension is {self.embedding_dimensions}.")
            else:
                self._client.create_collection(
                    collection_name=self.config.connectionSpecification.get('collection'),
                    vectors_config=VectorParams(size=self.embedding_dimensions, distance=distance)
                )
        except Exception as e:
            raise e
        return True, description

    def _create_client(self):
        url = self.config.connectionSpecification.get('url')
        self._client = QdrantClient(url)
