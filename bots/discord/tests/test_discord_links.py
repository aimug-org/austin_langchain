"""Tests for Discord link generation utilities."""

import pytest
from discord_bot.utils.discord_links import (
    generate_discord_message_link,
    generate_discord_channel_link,
    parse_discord_link,
    validate_discord_link
)


class TestDiscordLinkGeneration:
    """Test suite for Discord link utilities."""

    def test_generate_message_link(self):
        """Test generating Discord message link."""
        guild_id = "123456789"
        channel_id = "987654321"
        message_id = "555666777"

        link = generate_discord_message_link(guild_id, channel_id, message_id)

        assert link == "https://discord.com/channels/123456789/987654321/555666777"

    def test_generate_message_link_with_integers(self):
        """Test generating link with integer IDs."""
        link = generate_discord_message_link(123456789, 987654321, 555666777)

        assert link == "https://discord.com/channels/123456789/987654321/555666777"

    def test_generate_channel_link(self):
        """Test generating Discord channel link."""
        guild_id = "123456789"
        channel_id = "987654321"

        link = generate_discord_channel_link(guild_id, channel_id)

        assert link == "https://discord.com/channels/123456789/987654321"

    def test_parse_discord_link(self):
        """Test parsing Discord message link."""
        link = "https://discord.com/channels/123456789/987654321/555666777"

        parsed = parse_discord_link(link)

        assert parsed["guild_id"] == "123456789"
        assert parsed["channel_id"] == "987654321"
        assert parsed["message_id"] == "555666777"

    def test_parse_channel_link(self):
        """Test parsing Discord channel link (no message)."""
        link = "https://discord.com/channels/123456789/987654321"

        parsed = parse_discord_link(link)

        assert parsed["guild_id"] == "123456789"
        assert parsed["channel_id"] == "987654321"
        assert parsed["message_id"] is None

    def test_parse_invalid_link(self):
        """Test parsing invalid Discord link."""
        link = "https://example.com/not-a-discord-link"

        parsed = parse_discord_link(link)

        assert parsed is None

    def test_validate_discord_link_valid(self):
        """Test validating a valid Discord link."""
        link = "https://discord.com/channels/123456789/987654321/555666777"

        assert validate_discord_link(link) is True

    def test_validate_discord_link_invalid(self):
        """Test validating an invalid Discord link."""
        link = "https://example.com/not-discord"

        assert validate_discord_link(link) is False

    def test_validate_discord_link_malformed(self):
        """Test validating malformed Discord link."""
        link = "https://discord.com/channels/abc/def"  # Non-numeric IDs

        assert validate_discord_link(link) is False

    def test_generate_link_with_none_values(self):
        """Test that generating link with None raises error."""
        with pytest.raises((ValueError, TypeError)):
            generate_discord_message_link(None, "123", "456")

    def test_generate_link_with_empty_strings(self):
        """Test that generating link with empty strings raises error."""
        with pytest.raises(ValueError):
            generate_discord_message_link("", "123", "456")
