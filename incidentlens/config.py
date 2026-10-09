from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="IL_", env_file=ROOT / ".env", extra="ignore")
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ollama_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen3:4b"
    generator: str = "evidence"
    pdf_parser: str = "pdfplumber"
    pii_ner: bool = False
    llama_guard_model: str = ""
    data_dir: Path = ROOT / "data"
    model_dir: Path = ROOT / ".models"
    corpus_dir: Path = ROOT / "corpus"


settings = Settings()
