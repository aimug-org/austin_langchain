#!/usr/bin/env python3
"""Test fetching actual message history from accessible channels."""

import asyncio
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv()

async def test_message_fetch():
    """Test fetching message history."""
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.guild_messages = True
    intents.guild_reactions = True

    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print(f"✅ Bot connected: {bot.user}\n")

        for guild in bot.guilds:
            print(f"📍 Testing message history in: {guild.name}\n")

            # Test a few popular channels
            test_channels = ['off-topic', 'general', 'langchain', 'n8n', 'claude-code']

            for channel in guild.text_channels:
                if any(name in channel.name.lower() for name in test_channels):
                    bot_member = guild.get_member(bot.user.id)
                    channel_perms = channel.permissions_for(bot_member)

                    if not (channel_perms.read_messages and channel_perms.read_message_history):
                        print(f"❌ #{channel.name}: No permission")
                        continue

                    print(f"📋 Testing #{channel.name}:")

                    try:
                        # Fetch last 7 days of messages
                        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
                        messages = []

                        async for msg in channel.history(limit=100, after=cutoff):
                            messages.append(msg)

                        print(f"   ✅ Fetched {len(messages)} messages from last 7 days")

                        if messages:
                            latest = messages[0]
                            print(f"   📝 Latest message:")
                            print(f"      Author: {latest.author.name}")
                            print(f"      Time: {latest.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                            print(f"      Content: {latest.content[:100]}...")
                            print(f"      Reactions: {len(latest.reactions)}")

                            # Check if we can read content
                            if latest.content:
                                print(f"      ✅ Can read message content")
                            else:
                                print(f"      ⚠️  Message has no text content (might be embed/attachment)")
                        else:
                            print(f"   📭 No messages in last 7 days")

                        print()

                    except discord.Forbidden:
                        print(f"   ❌ Forbidden: Cannot fetch history")
                    except Exception as e:
                        print(f"   ❌ Error: {type(e).__name__}: {e}")

                    # Only test a few channels
                    if len([c for c in guild.text_channels if any(n in c.name.lower() for n in test_channels)]) >= 3:
                        break

        print("\n✅ History fetch test complete!")
        await bot.close()

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN not found!")
        return

    try:
        await bot.start(token)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_message_fetch())
