"""Settings for Trello MCP."""

from pydantic_settings import BaseSettings
import logging

# Configure logging to only show WARNING and above
logging.basicConfig(level=logging.WARNING)

class TrelloSettings(BaseSettings):
    """Server configuration settings."""
    
    # Trello API settings with default values
    TRELLO_API_KEY: str = ""
    TRELLO_TOKEN: str = ""
    TRELLO_API_BASE_URL: str = "https://api.trello.com/1"


# Create settings instance for import
settings = TrelloSettings()
