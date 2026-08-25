from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "DeepResearch"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-32-chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "deepresearch"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    # Qdrant
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333

    # LiteLLM Gateway — provider API keys loaded from environment only, never hardcoded
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None

    # LiteLLM Gateway — model configuration
    LITELLM_DEFAULT_MODEL: str = "gpt-4o-mini"
    LITELLM_FALLBACK_MODEL: str = "gpt-3.5-turbo"
    LITELLM_TIMEOUT_SECONDS: int = 60
    LITELLM_MAX_RETRIES: int = 3
    LITELLM_ENABLE_COST_TRACKING: bool = True

    # Ingestion & Semantic Chunking Configuration
    CHUNK_TARGET_SIZE: int = 1000  # Target characters per chunk
    CHUNK_MAX_SIZE: int = 1500  # Max hard boundary characters per chunk
    CHUNK_OVERLAP: int = 150  # Overlap characters for sliding window fallback

    # Vector Store & Embedding Configuration
    QDRANT_COLLECTION_NAME: str = "deepresearch_chunks"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_FALLBACK_MODEL: str = "text-embedding-ada-002"
    EMBEDDING_DIMENSION: int = 1536
    HYBRID_SEARCH_DENSE_WEIGHT: float = 0.7
    HYBRID_SEARCH_SPARSE_WEIGHT: float = 0.3
    RRF_K_CONSTANT: int = 60

    @property
    def QDRANT_URL(self) -> str:
        return f"http://{self.QDRANT_HOST}:{self.QDRANT_PORT}"



    @property
    def REDIS_URI(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def POSTGRES_URI(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()

