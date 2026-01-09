"""
GravityWork Backend - FastAPI Application
AI-Native Project Orchestration Platform
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings

from routers import chat, integrations, health


class Settings(BaseSettings):
    """Application settings loaded from environment."""
    
    app_name: str = "GravityWork"
    debug: bool = False
    
    # AI Provider
    ai_provider: str = "openai"  # openai, gemini, openrouter
    openai_api_key: str = ""
    gemini_api_key: str = ""
    
    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "gravitywork_docs"
    
    # Integrations
    jira_url: str = ""
    jira_email: str = ""
    jira_token: str = ""
    
    slack_bot_token: str = ""
    slack_app_token: str = ""
    
    github_token: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("starting_gravitywork", version="0.1.0")
    
    # Startup: Initialize connections
    yield
    
    # Shutdown: Cleanup
    logger.info("shutting_down_gravitywork")


app = FastAPI(
    title="GravityWork API",
    description="AI-Native Project Orchestration Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
