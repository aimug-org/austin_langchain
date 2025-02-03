"""Settings for LangGraph MCP."""

from pydantic_settings import BaseSettings
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING)

class Settings(BaseSettings):
    """Settings for LangGraph MCP."""
    
    # Server settings
    PORT: int = 50827
    URL: str = f"http://localhost:{PORT}"
