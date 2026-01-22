import os

from loguru import logger

from genai_services.part2.project_2_rag.repository import VectorDBRepository
from genai_services.part2.project_2_rag.transform import clean, embed, load


class VectorDBService(VectorDBRepository):
    """Service for vector database operations."""

    def __init__(self) -> None:
        """Initialize the vector database client."""
        super().__init__()

    async def store_file_content_in_db(
        self,
        filepath: str,
        chunk_size: int = 512,
        collection_name: str = "knowledgebase",
        collection_size: int = 768,
    ) -> None:
        """Store the content of a file in the vector database."""
        await self.create_collection(collection_name, collection_size)
        logger.info(f"Inserting content of {filepath} into database")
        async for chunk in load(filepath, chunk_size):
            logger.info(f"Inserting chunk of {chunk[0:20]} characters into database")

            embedding_vector: list[float] = embed(clean(chunk))
            filename: str = os.path.basename(filepath)
            await self.create(
                collection_name=collection_name,
                embedding_vector=embedding_vector,
                original_text=chunk,
                source=filename,
            )
        logger.success(f"Content of {filepath} inserted into database")
