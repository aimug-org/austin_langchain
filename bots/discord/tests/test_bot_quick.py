#!/usr/bin/env python3
"""Quick Discord bot permission checker that exits automatically."""

import asyncio
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

async def check_permissions():
    """Check bot permissions and exit."""
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.guild_messages = True
    intents.guild_reactions = True

    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print(f"✅ Bot connected: {bot.user}")
        print(f"🆔 Bot ID: {bot.user.id}\n")

        for guild in bot.guilds:
            print(f"📍 Guild: {guild.name} (ID: {guild.id})")
            print(f"   Members: {guild.member_count}")

            bot_member = guild.get_member(bot.user.id)
            if not bot_member:
                print("   ❌ Bot is not a member!")
                continue

            perms = bot_member.guild_permissions
            print(f"\n   🔑 Bot Permissions:")
            print(f"      {'✅' if perms.read_messages else '❌'} Read Messages")
            print(f"      {'✅' if perms.read_message_history else '❌'} Read Message History")
            print(f"      {'✅' if perms.view_channel else '❌'} View Channels")
            print(f"      {'✅' if perms.send_messages else '❌'} Send Messages")

            # Test channel access
            print(f"\n   📋 Testing Channels (first 5):")
            text_channels = [ch for ch in guild.channels if isinstance(ch, discord.TextChannel)]

            for channel in text_channels[:5]:
                channel_perms = channel.permissions_for(bot_member)
                can_read = channel_perms.read_messages and channel_perms.read_message_history
                print(f"      {'✅' if can_read else '❌'} #{channel.name}")

                if can_read:
                    try:
                        # Try to fetch one message
                        messages = [msg async for msg in channel.history(limit=1)]
                        if messages:
                            print(f"         ✅ Can fetch history (last msg: {messages[0].created_at.strftime('%Y-%m-%d %H:%M')})")
                        else:
                            print(f"         📭 Channel empty")
                    except discord.Forbidden:
                        print(f"         ❌ Forbidden (check permissions)")
                    except Exception as e:
                        print(f"         ⚠️  Error: {type(e).__name__}")

            if len(text_channels) > 5:
                print(f"      ... and {len(text_channels) - 5} more channels\n")

        print("\n✅ Permission check complete!")
        await bot.close()

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN not found!")
        return

    try:
        await bot.start(token)
    except discord.LoginFailure:
        print("❌ Invalid bot token!")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(check_permissions())
