"""Utilities for generating and parsing Discord links."""

from typing import Dict, Optional, Union
import re


def generate_discord_message_link(
    guild_id: Union[str, int],
    channel_id: Union[str, int],
    message_id: Union[str, int]
) -> str:
    """
    Generate a Discord message link.

    Args:
        guild_id: Discord guild (server) ID
        channel_id: Discord channel ID
        message_id: Discord message ID

    Returns:
        Discord message URL

    Raises:
        ValueError: If any ID is empty or None
        TypeError: If IDs cannot be converted to string

    Examples:
        >>> generate_discord_message_link("123", "456", "789")
        'https://discord.com/channels/123/456/789'
    """
    if guild_id is None or channel_id is None or message_id is None:
        raise ValueError("Guild ID, channel ID, and message ID are required")

    guild_str = str(guild_id).strip()
    channel_str = str(channel_id).strip()
    message_str = str(message_id).strip()

    if not guild_str or not channel_str or not message_str:
        raise ValueError("Guild ID, channel ID, and message ID cannot be empty")

    return f"https://discord.com/channels/{guild_str}/{channel_str}/{message_str}"


def generate_discord_channel_link(
    guild_id: Union[str, int],
    channel_id: Union[str, int]
) -> str:
    """
    Generate a Discord channel link.

    Args:
        guild_id: Discord guild (server) ID
        channel_id: Discord channel ID

    Returns:
        Discord channel URL

    Raises:
        ValueError: If any ID is empty or None

    Examples:
        >>> generate_discord_channel_link("123", "456")
        'https://discord.com/channels/123/456'
    """
    if guild_id is None or channel_id is None:
        raise ValueError("Guild ID and channel ID are required")

    guild_str = str(guild_id).strip()
    channel_str = str(channel_id).strip()

    if not guild_str or not channel_str:
        raise ValueError("Guild ID and channel ID cannot be empty")

    return f"https://discord.com/channels/{guild_str}/{channel_str}"


def parse_discord_link(link: str) -> Optional[Dict[str, Optional[str]]]:
    """
    Parse a Discord link into its components.

    Args:
        link: Discord URL to parse

    Returns:
        Dictionary with guild_id, channel_id, and message_id (if present)
        Returns None if link is not a valid Discord link

    Examples:
        >>> parse_discord_link("https://discord.com/channels/123/456/789")
        {'guild_id': '123', 'channel_id': '456', 'message_id': '789'}
        >>> parse_discord_link("https://discord.com/channels/123/456")
        {'guild_id': '123', 'channel_id': '456', 'message_id': None}
    """
    if not link or not isinstance(link, str):
        return None

    # Pattern for Discord message link
    message_pattern = r'https://discord\.com/channels/(\d+)/(\d+)/(\d+)'
    # Pattern for Discord channel link
    channel_pattern = r'https://discord\.com/channels/(\d+)/(\d+)$'

    # Try message link first
    match = re.match(message_pattern, link)
    if match:
        return {
            "guild_id": match.group(1),
            "channel_id": match.group(2),
            "message_id": match.group(3)
        }

    # Try channel link
    match = re.match(channel_pattern, link)
    if match:
        return {
            "guild_id": match.group(1),
            "channel_id": match.group(2),
            "message_id": None
        }

    return None


def validate_discord_link(link: str) -> bool:
    """
    Validate if a string is a valid Discord link.

    Args:
        link: String to validate

    Returns:
        True if valid Discord link, False otherwise

    Examples:
        >>> validate_discord_link("https://discord.com/channels/123/456/789")
        True
        >>> validate_discord_link("https://example.com")
        False
    """
    parsed = parse_discord_link(link)
    return parsed is not None
