#!/usr/bin/env python3
"""
Basic Discord bot connection test.
Tests if the bot can connect without privileged intents.
"""

import asyncio
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BasicTestBot(commands.Bot):
    """Test bot to check basic Discord connection."""
    
    def __init__(self):
        # Use only non-privileged intents
        intents = discord.Intents.default()
        # Don't use message_content (privileged)
        # intents.message_content = True
        
        print("🔧 Using basic intents (no privileged intents)")
        print(f"   - guilds: {intents.guilds}")
        print(f"   - guild_messages: {intents.guild_messages}")
        print()
        
        super().__init__(command_prefix='!', intents=intents)
        
    async def on_ready(self):
        """Called when bot is ready."""
        print(f"\n✅ Bot connected successfully!")
        print(f"🤖 Bot name: {self.user}")
        print(f"🆔 Bot ID: {self.user.id}")
        print(f"🏠 Connected to {len(self.guilds)} guild(s)\n")
        
        # Check guilds
        for guild in self.guilds:
            print(f"📍 Guild: {guild.name} (ID: {guild.id})")
            print(f"   Members: {guild.member_count}")
            
            # Get bot member
            bot_member = guild.get_member(self.user.id)
            if not bot_member:
                print("   ❌ Bot is not a member of this guild!")
                continue
            
            # Check text channels
            text_channels = [ch for ch in guild.channels if isinstance(ch, discord.TextChannel)]
            print(f"   📋 Found {len(text_channels)} text channels")
            
            # Test message access WITHOUT content intent
            accessible_channels = 0
            for channel in text_channels[:5]:  # Test first 5 channels
                perms = channel.permissions_for(bot_member)
                if perms.read_messages and perms.read_message_history:
                    accessible_channels += 1
                    print(f"      ✅ Can access #{channel.name}")
                    
                    # Try to fetch message metadata (not content)
                    try:
                        message_count = 0
                        async for msg in channel.history(limit=5):
                            message_count += 1
                        print(f"         📊 Found {message_count} recent messages")
                    except discord.Forbidden:
                        print(f"         ❌ Cannot fetch history (Forbidden)")
                    except Exception as e:
                        print(f"         ⚠️  Error: {type(e).__name__}")
                else:
                    print(f"      ❌ Cannot access #{channel.name}")
            
            print(f"\n   📊 Summary: Can access {accessible_channels}/{len(text_channels[:5])} tested channels")
            print()
        
        print("\n⚠️  Note: Without 'message_content' intent, the bot cannot read message text.")
        print("   To read message content, you need to:")
        print("   1. Go to https://discord.com/developers/applications/")
        print("   2. Select your application")
        print("   3. Go to 'Bot' section")
        print("   4. Enable 'MESSAGE CONTENT INTENT' under 'Privileged Gateway Intents'")
        print("   5. Save changes")
        
        await self.close()

async def main():
    """Run the basic test bot."""
    print("🤖 Basic Discord Connection Test")
    print("=" * 40)
    
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN not found in environment variables!")
        return
    
    bot = BasicTestBot()
    
    try:
        await bot.start(token)
    except discord.LoginFailure:
        print("❌ Invalid bot token! Check your DISCORD_TOKEN.")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())