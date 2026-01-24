from fastapi import Body

from genai_services.part1.schemas import TextModelRequest

from .transform import clean, embed
from .vector_service import VectorDBService

_body_default = Body(..., description="Text model request")


async def get_rag_content(
    body: TextModelRequest = _body_default,
) -> str:
    """Get RAG content from the vector database."""
    vector_service = VectorDBService()
    cleaned_prompt = clean(body.prompt)
    embedding_vector: list[float] = embed(cleaned_prompt)
    rag_content = await vector_service.search(
        collection_name="knowledgebase",
        query_vector=embedding_vector,
        retrieval_limit=3,
        score_threshold=0.7,
    )
    rag_content_str: str = "\n".join(
        [
            result.payload["original_text"]
            for result in rag_content
            if result.payload is not None
        ]
    )
    return rag_content_str
