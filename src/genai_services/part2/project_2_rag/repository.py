from loguru import logger
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import (
    CollectionsResponse,
    CountResult,
    QueryResponse,
    ScoredPoint,
)


class VectorDBRepository:
    """Repository for vector database operations."""

    def __init__(self, host: str = "localhost", port: int = 6333) -> None:
        """Initialize the vector database client."""
        self.db_client = AsyncQdrantClient(host=host, port=port)

    async def create_collection(self, collection_name: str, size: int) -> bool:
        """Create a new collection in the vector database."""
        vectors_config = models.VectorParams(size=size, distance=models.Distance.COSINE)

        response: CollectionsResponse = await self.db_client.get_collections()

        collections_exist: bool = any(
            collection.name == collection_name for collection in response.collections
        )

        if collections_exist:
            logger.info(
                f"Collection {collection_name} already exists - recreating collection"
            )

            await self.db_client.recreate_collection(
                collection_name=collection_name, vectors_config=vectors_config
            )

        logger.debug(f"Creating collection {collection_name}")
        return await self.db_client.create_collection(
            collection_name=collection_name, vectors_config=vectors_config
        )

    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection from the vector database."""
        logger.debug(f"Deleting collection {collection_name}")
        return await self.db_client.delete_collection(collection_name=collection_name)

    async def create(
        self,
        collection_name: str,
        embedding_vector: list[float],
        original_text: str,
        source: str,
    ) -> None:
        """Create a new vector in the vector database."""
        response: CountResult = await self.db_client.count(
            collection_name=collection_name
        )
        logger.debug(
            f"Creating a new vector with ID {response.count}"
            f"in collection {collection_name}"
        )
        await self.db_client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=response.count,
                    vector=embedding_vector,
                    payload={
                        "original_text": original_text,
                        "source": source,
                    },
                )
            ],
        )
        logger.debug("Vector created successfully")

    async def search(
        self,
        collection_name: str,
        query_vector: list[float],
        retrieval_limit: int,
        score_threshold: float,
    ) -> list[ScoredPoint]:
        logger.debug(
            f"Searching for relevant items in the {collection_name} collection"
        )
        response: QueryResponse = await self.db_client.query_points(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=retrieval_limit,
            score_threshold=score_threshold,
        )
        return response.points
