#!/usr/bin/env python3
"""Check ALL channels to find which ones are accessible."""

import asyncio
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

async def check_all_channels():
    """Check all channel permissions."""
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
            print(f"📍 Guild: {guild.name}\n")

            bot_member = guild.get_member(bot.user.id)
            if not bot_member:
                print("❌ Bot is not a member!")
                await bot.close()
                return

            text_channels = [ch for ch in guild.channels if isinstance(ch, discord.TextChannel)]

            accessible = []
            restricted = []

            for channel in text_channels:
                channel_perms = channel.permissions_for(bot_member)
                can_read = channel_perms.read_messages and channel_perms.read_message_history

                if can_read:
                    accessible.append(channel.name)
                else:
                    restricted.append(channel.name)

            print(f"✅ ACCESSIBLE CHANNELS ({len(accessible)}):")
            if accessible:
                for name in accessible:
                    print(f"   ✅ #{name}")
            else:
                print("   ⚠️  NONE - Bot has no channel access!")

            print(f"\n❌ RESTRICTED CHANNELS ({len(restricted)}):")
            for name in restricted[:10]:
                print(f"   ❌ #{name}")
            if len(restricted) > 10:
                print(f"   ... and {len(restricted) - 10} more")

            print(f"\n📊 Summary:")
            print(f"   Total channels: {len(text_channels)}")
            print(f"   Accessible: {len(accessible)}")
            print(f"   Restricted: {len(restricted)}")

            if len(accessible) == 0:
                print(f"\n⚠️  ACTION REQUIRED:")
                print(f"   The bot needs a role with 'View Channels' permission")
                print(f"   Or add the bot to specific channels you want to monitor")

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
    asyncio.run(check_all_channels())
