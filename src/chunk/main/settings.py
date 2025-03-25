from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.chunk.main.constants import MAX_CHUNK_SIZE


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    debug: bool = False
    title: str = "Chunked-Flow"
    version: str = "0.0.2"

    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(levelname)s - %(message)s"

    db_password: str
    db_user: str
    db_name: str
    db_host: str = "localhost"
    db_port: int = 5432
    db: str = "postgresql"
    db_table_name: str

    concurrency_limit: int = 10
    chunk_size: int = 10
    offset_initial: int | None = None

    aws_bucket: str = ""
    aws_region: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    metadata_file_name: str = "metadata_{timestamp}.json"

    @field_validator("chunk_size")
    @classmethod
    def max_chunk_size(cls, v: int) -> int:
        """
        Validates the `chunk_size` field to ensure the provided value does not exceed the maximum
        allowed chunk size.
        """
        if v > MAX_CHUNK_SIZE:
            return MAX_CHUNK_SIZE
        return v

    @property
    def dsn(self) -> str:
        """
        Constructs and returns the Data Source Name (DSN) string.
        """
        return f"{self.db}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


@lru_cache
def get_settings() -> Settings:
    """
    Retrieves an instance of the Settings.
    """
    return Settings()
