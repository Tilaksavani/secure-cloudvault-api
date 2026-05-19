from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    storage_backend: str = "local"
    database_url: str = "sqlite:///./file_metadata.db"

    local_storage_dir: str = "local_storage"
    max_file_size_mb: int = 10

    aws_region: str = "us-east-1"
    aws_s3_bucket: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
