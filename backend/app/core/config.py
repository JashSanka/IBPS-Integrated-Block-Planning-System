"""
Core Server Configuration for FastAPI.
"""

import os
from typing import List
from pydantic import BaseModel, Field


class ServerSettings(BaseModel):
    """FastAPI server and CORS settings."""
    app_name: str = "IBPS — Integrated Block Planning System"
    app_version: str = "1.0.0"
    api_prefix: str = "/api"
    debug: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    
    # Configurable CORS origins
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000"
            ).split(",")
            if origin.strip()
        ]
    )


server_settings = ServerSettings()
