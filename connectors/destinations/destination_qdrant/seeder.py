import uuid
from qdrant_client import QdrantClient, models
from typing import Any, List, Optional, Dict
from connectors.destinations.vector_db_helpers.seeder import Seeder
from qdrant_openapi_client.models import VectorParams, Distance
from pydantic_models.dat_message import DatDocumentMessage
from pydantic_models.stream_metadata import StreamMetadata


DISTANCE_MAP = {
    "dot": Distance.DOT,
    "cos": Distance.COSINE,
    "euc": Distance.EUCLID,
}

class QdrantSeeder(Seeder):
    def __init__(self, config: Any, embedding_dimensions: int):
        super().__init__(config)
        self.embedding_dimensions = embedding_dimensions
        self._create_client()

    def seed(self, document_chunks: List[DatDocumentMessage], namespace: str, stream: str) -> None:
        points = []
        for document_chunk in document_chunks:
            metadata = document_chunk.data.metadata.model_dump()
            chunk = document_chunk.data.vectors
            points.append(
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=chunk,
                    payload=metadata
                )
            )
        self._client.upload_points(
            collection_name=self.config.connectionSpecification.get('collection'),
            points=points
        )

    def delete(self, filter, namespace=None):
        should_filter = self.metadata_filter(filter.model_dump())
        self._client.delete(
            collection_name=self.config.connectionSpecification.get('collection'),
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    should=should_filter
                ),
            )
        )
        # scroll_records = self.scroll(scroll_filter=should_filter)
        # for point in scroll_records:
        #     delete_ids.append(point.id)


    def check(self) -> Optional[str]:
        try:
            if not self._client:
                return (False, "Qdrant is not alive")
            available_collections = [collection.name for collection in self._client.get_collections().collections]
            distance = DISTANCE_MAP.get(self.config.connectionSpecification.get('distance'))
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
        print(f"Qdrant url: {url}")
        self._client = QdrantClient(url)
    
    def scroll(self, scroll_filter: List[models.FieldCondition]):
        scroll_records = self._client.scroll(
            collection_name=self.config.connectionSpecification.get('collection'),
            scroll_filter=models.Filter(
                should=scroll_filter
            ),
        )
        return scroll_records[0]

    def metadata_filter(self, metadata: Dict[Any, str]) -> Any:
        should_fields = []
        for field in self.METADATA_FILTER_FIELDS:
            if field in metadata:
                should_fields.append(models.FieldCondition(
                    key=field,
                    match=models.MatchValue(value=metadata[field])
                ))
        return should_fields
