"""Configuration management for the Discord bot."""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Environment
    environment: str = Field(default="development", description="Environment (development, staging, production)")
    debug: bool = Field(default=False, description="Debug mode")
    testing: bool = Field(default=False, description="Testing mode")
    
    # Discord Configuration
    discord_token: str = Field(description="Discord bot token")
    discord_guild_id: Optional[str] = Field(default=None, description="Discord guild ID")
    discord_channel_ids: str = Field(default="", description="Comma-separated channel IDs to monitor")
    discord_rate_limit_requests: int = Field(default=50, description="Discord API rate limit requests")
    discord_rate_limit_period: int = Field(default=60, description="Discord API rate limit period")
    
    # Database Configuration
    database_url: str = Field(description="Database connection URL")
    database_pool_size: int = Field(default=5, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Database max overflow connections")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    
    # LangSmith Configuration
    langchain_tracing_v2: bool = Field(default=True, description="Enable LangSmith tracing")
    langchain_api_key: Optional[str] = Field(default=None, description="LangSmith API key")
    langchain_project: str = Field(default="austin-langchain-discord-bot", description="LangSmith project name")
    
    # Model Router Configuration
    requesty_api_key: Optional[str] = Field(default=None, description="Requesty.ai API key")
    requesty_base_url: str = Field(default="https://api.requesty.ai/v1", description="Requesty.ai base URL")
    
    # Default Models
    default_research_model: str = Field(default="claude-3-sonnet-20240229", description="Default model for research tasks")
    default_writing_model: str = Field(default="claude-3-sonnet-20240229", description="Default model for writing tasks")
    default_editing_model: str = Field(default="claude-3-haiku-20240307", description="Default model for editing tasks")
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")

    # Perplexity Configuration
    perplexity_api_key: Optional[str] = Field(default=None, description="Perplexity API key")
    perplexity_base_url: str = Field(default="https://api.perplexity.ai", description="Perplexity base URL")
    
    # Buttondown Configuration
    buttondown_api_key: Optional[str] = Field(default=None, description="Buttondown API key")
    buttondown_base_url: str = Field(default="https://api.buttondown.email/v1", description="Buttondown base URL")
    
    # Newsletter Configuration
    newsletter_schedule_daily: str = Field(default="0 6 * * *", description="Daily newsletter cron schedule")
    newsletter_schedule_weekly: str = Field(default="0 20 * * 6", description="Weekly newsletter cron schedule - Saturday 8pm")
    newsletter_schedule_monthly: str = Field(default="0 20 1 * *", description="Monthly newsletter cron schedule - 1st day 8pm")
    timezone: str = Field(default="America/Chicago", description="Timezone for scheduling")
    
    # Rate Limiting
    api_rate_limit_requests: int = Field(default=100, description="General API rate limit requests")
    api_rate_limit_period: int = Field(default=60, description="General API rate limit period")
    
    # Content Configuration
    max_discussion_age_days: int = Field(default=7, description="Maximum age of discussions to consider")
    min_engagement_score: float = Field(default=1.0, description="Minimum engagement score for inclusion")
    max_newsletter_length: int = Field(default=5000, description="Maximum newsletter length in words")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")
    
    # Security
    secret_key: str = Field(description="Secret key for encryption")
    allowed_hosts: List[str] = Field(default=["localhost", "127.0.0.1"], description="Allowed hosts")
    
    @property
    def channel_ids(self) -> List[str]:
        """Get list of channel IDs to monitor.
        
        Returns:
            List of channel IDs, or ['ALL'] if all channels should be monitored.
        """
        if not self.discord_channel_ids:
            return []
        
        # Check if user wants to monitor all channels
        if self.discord_channel_ids.strip().upper() == "ALL":
            return ["ALL"]
            
        return [cid.strip() for cid in self.discord_channel_ids.split(",") if cid.strip()]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"
    
    def model_dump_safe(self) -> dict:
        """Return settings without sensitive information."""
        data = self.model_dump()
        sensitive_keys = [
            "discord_token",
            "database_url",
            "langchain_api_key",
            "requesty_api_key",
            "openai_api_key",
            "perplexity_api_key",
            "buttondown_api_key",
            "secret_key"
        ]
        for key in sensitive_keys:
            if key in data and data[key]:
                data[key] = "*" * 8
        return data


# Global settings instance
settings = Settings()