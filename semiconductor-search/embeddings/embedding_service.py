"""
Generates OpenAI vector embeddings for product feature texts.

When OPENAI_API_KEY is not set, embedding generation is skipped gracefully.
The rest of the system (ingestion, structured search) remains fully functional.
"""

from config.settings import OPENAI_API_KEY, EMBEDDING_MODEL


def get_embedding(text: str) -> list[float] | None:
    """
    Generate a single embedding vector for the given text using OpenAI.

    Returns:
        List of floats (the embedding vector), or None if the API key is missing
        or an error occurs.
    """
    if not OPENAI_API_KEY:
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"[Embedding] Error generating embedding: {e}")
        return None


def get_embeddings_batch(texts: list[str]) -> list[list[float] | None]:
    """
    Generate embeddings for a list of texts in a single API call (more efficient).

    Returns:
        List of embedding vectors (or None values where generation failed).
    """
    if not OPENAI_API_KEY:
        return [None] * len(texts)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
        )
        # The API returns embeddings in the same order as the input
        result = [None] * len(texts)
        for item in response.data:
            result[item.index] = item.embedding
        return result
    except Exception as e:
        print(f"[Embedding] Batch error: {e}")
        return [None] * len(texts)
