import os

# Database connection string (uses Replit's built-in PostgreSQL)
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# OpenAI API key - optional, embeddings are skipped when not provided
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Embedding model to use
EMBEDDING_MODEL = "text-embedding-3-small"

# Embedding vector dimension for the model above
EMBEDDING_DIMENSION = 1536

# Number of top alternatives to return by default
TOP_N_RESULTS = 10
