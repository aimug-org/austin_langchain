from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class TrelloSettings(BaseSettings):
    """Server configuration settings loaded from environment variables."""
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

    TRELLO_API_KEY: str
    TRELLO_TOKEN: str
    TRELLO_BOARD_ID: Optional[str] = None
    TRELLO_API_BASE_URL: str = "https://api.trello.com/1"

settings = TrelloSettings()
