from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(alias="DATABASE_URL")
    openai_api_key: SecretStr | None = Field(default=None, alias="OPENAI_API_KEY")
    storage_dir: Path = Field(default=Path("var/storage"), alias="PAPER_STORAGE_DIR")
    repository_root: Path = Field(default=Path.cwd(), alias="PAPER_REPOSITORY_ROOT")
    worker_id: str = Field(default="local-worker", alias="PAPER_WORKER_ID")

    model_fast: str = Field(default="gpt-5.6-luna", alias="PAPER_MODEL_FAST")
    model_standard: str = Field(default="gpt-5.6-terra", alias="PAPER_MODEL_STANDARD")
    model_deep: str = Field(default="gpt-5.6-sol", alias="PAPER_MODEL_DEEP")
    model_embedding: str = Field(
        default="text-embedding-3-large", alias="PAPER_MODEL_EMBEDDING"
    )
    embedding_dimensions: int = Field(default=1536, alias="PAPER_EMBEDDING_DIMENSIONS")

    budget_triage_usd: float = Field(default=0.10, alias="PAPER_BUDGET_TRIAGE_USD")
    budget_standard_usd: float = Field(default=1.0, alias="PAPER_BUDGET_STANDARD_USD")
    budget_deep_usd: float = Field(default=5.0, alias="PAPER_BUDGET_DEEP_USD")
    budget_research_usd: float = Field(default=10.0, alias="PAPER_BUDGET_RESEARCH_USD")
    budget_roadmap_usd: float = Field(default=20.0, alias="PAPER_BUDGET_ROADMAP_USD")
    web_search_cost_usd: float = Field(default=0.01, alias="PAPER_WEB_SEARCH_COST_USD")

    poll_interval_seconds: float = 1.5
    job_lease_seconds: int = 300
    max_job_attempts: int = 3

    def prepare_runtime(self) -> None:
        for child in ("documents", "snapshots", "page-images", "tmp"):
            (self.storage_dir / child).mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
