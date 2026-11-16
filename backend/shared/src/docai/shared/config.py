"""Cấu hình tối thiểu cho API DocAI."""

import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    api_title: str = "DocAI"
    api_version: str = "0.1.0"
    debug: bool = Field(default_factory=lambda: os.getenv("DOCAI_DEBUG", "0") == "1")


settings = Settings()
