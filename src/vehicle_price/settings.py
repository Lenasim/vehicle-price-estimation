from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="API_", extra="ignore")
    model_pipeline_path: Path = Path("artifacts/model_pipeline.joblib")
    metadata_path: Path = Path("artifacts/metadata.json")
    inference_concurrency: int = Field(default=4, ge=1, le=32)
