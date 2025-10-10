"""Logging configuration for the Discord bot."""

import sys
import json
from typing import Any, Dict
from loguru import logger
from discord_bot.core.config import settings


def json_formatter(record: Dict[str, Any]) -> str:
    """Format log record as JSON."""
    log_entry = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "logger": record["name"],
        "message": record["message"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
    }

    # Add extra fields if present, but skip logger_name since it's redundant
    if "extra" in record:
        extra_data = record["extra"]
        # Get direct extra values, skip internal loguru fields and nested extra
        for key, value in extra_data.items():
            if not key.startswith("_") and key not in ["extra", "logger_name"]:
                # Convert non-serializable types to strings
                try:
                    json.dumps({key: value})
                    log_entry[key] = value
                except (TypeError, ValueError):
                    log_entry[key] = str(value)

    return json.dumps(log_entry) + "\n"


def setup_logging() -> None:
    """Configure logging for the application."""

    # Remove default handler
    logger.remove()

    # Determine log level
    log_level = settings.log_level.upper()

    # Choose formatter based on log format
    if settings.log_format == "json":
        # Use custom JSON formatter
        logger.add(
            sys.stderr,
            format=json_formatter,
            level=log_level,
            colorize=False,
        )

        # Add file handler for production
        if settings.is_production:
            logger.add(
                "logs/discord_bot.log",
                format=json_formatter,
                level=log_level,
                rotation="1 day",
                retention="30 days",
                compression="gz",
            )

            # Separate error log
            logger.add(
                "logs/discord_bot_errors.log",
                format=json_formatter,
                level="ERROR",
                rotation="1 day",
                retention="30 days",
                compression="gz",
            )
    else:
        # Use text formatter
        text_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

        logger.add(
            sys.stderr,
            format=text_format,
            level=log_level,
            colorize=True,
        )

        # Add file handler for production
        if settings.is_production:
            logger.add(
                "logs/discord_bot.log",
                format=text_format,
                level=log_level,
                rotation="1 day",
                retention="30 days",
                compression="gz",
                colorize=False,
            )

            # Separate error log
            logger.add(
                "logs/discord_bot_errors.log",
                format=text_format,
                level="ERROR",
                rotation="1 day",
                retention="30 days",
                compression="gz",
                colorize=False,
            )

    # Suppress noisy third-party loggers in production
    if settings.is_production:
        logger.disable("discord")
        logger.disable("httpx")
        logger.disable("httpcore")

    logger.info(
        "Logging configured",
        extra={
            "log_level": log_level,
            "log_format": settings.log_format,
            "environment": settings.environment,
        }
    )


def get_logger(name: str):
    """Get a logger instance with the given name."""
    return logger.bind(logger_name=name)