#!/usr/bin/env python3
"""
Simple Discord bot permission checker.
Tests if the bot can connect and read messages from channels.
"""

import asyncio
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

class PermissionTestBot(commands.Bot):
    """Test bot to check Discord permissions."""
    
    def __init__(self):
        # Configure intents
        intents = discord.Intents.default()
        intents.message_content = True  # Required to read message content
        intents.guilds = True
        intents.guild_messages = True
        intents.guild_reactions = True
        # Don't request members intent if not needed
        # intents.members = True
        
        print("🔧 Configured intents:")
        print(f"   - message_content: {intents.message_content}")
        print(f"   - guilds: {intents.guilds}")
        print(f"   - guild_messages: {intents.guild_messages}")
        print(f"   - guild_reactions: {intents.guild_reactions}")
        print()
        
        super().__init__(command_prefix='!', intents=intents)
        
    async def on_ready(self):
        """Called when bot is ready."""
        print(f"\n✅ Bot connected as: {self.user}")
        print(f"🆔 Bot ID: {self.user.id}")
        print(f"🏠 Connected to {len(self.guilds)} guild(s)\n")
        
        # Check each guild
        for guild in self.guilds:
            print(f"📍 Guild: {guild.name} (ID: {guild.id})")
            print(f"   Members: {guild.member_count}")
            
            # Get bot member in this guild
            bot_member = guild.get_member(self.user.id)
            if not bot_member:
                print("   ❌ Bot is not a member of this guild!")
                continue
                
            # Check bot permissions
            print(f"\n   🔑 Bot Permissions in {guild.name}:")
            perms = bot_member.guild_permissions
            
            critical_perms = [
                ("Read Messages", perms.read_messages),
                ("Read Message History", perms.read_message_history),
                ("View Channels", perms.view_channel),
                ("Send Messages", perms.send_messages),
                ("Add Reactions", perms.add_reactions),
            ]
            
            for perm_name, has_perm in critical_perms:
                status = "✅" if has_perm else "❌"
                print(f"      {status} {perm_name}")
            
            # Check each text channel
            print(f"\n   📋 Channel Permissions:")
            text_channels = [ch for ch in guild.channels if isinstance(ch, discord.TextChannel)]
            
            for channel in text_channels[:10]:  # Check first 10 channels
                channel_perms = channel.permissions_for(bot_member)
                can_read = channel_perms.read_messages and channel_perms.read_message_history
                status = "✅" if can_read else "❌"
                print(f"      {status} #{channel.name}")
                
                # Try to fetch a message if we can read
                if can_read:
                    try:
                        messages = []
                        async for msg in channel.history(limit=1):
                            messages.append(msg)
                        
                        if messages:
                            print(f"         📝 Can fetch messages (last: {messages[0].created_at})")
                        else:
                            print(f"         📭 Channel is empty")
                    except discord.Forbidden:
                        print(f"         ❌ Cannot fetch messages (Forbidden)")
                    except Exception as e:
                        print(f"         ⚠️  Error fetching messages: {type(e).__name__}")
            
            if len(text_channels) > 10:
                print(f"      ... and {len(text_channels) - 10} more channels")
            
            print()  # Blank line between guilds
        
        # Test message monitoring
        print("\n🔍 Testing message monitoring capability...")
        print("   Send a test message in any channel to verify bot can read it.")
        print("   Bot will echo back if it can see the message.")
        print("   Press Ctrl+C to stop the test.\n")
        
    async def on_message(self, message):
        """Test message reading."""
        # Skip bot's own messages
        if message.author.bot:
            return
        
        print(f"📨 Message received!")
        print(f"   Channel: #{message.channel.name}")
        print(f"   Author: {message.author.name}")
        print(f"   Content: {message.content[:100]}...")
        print(f"   Can read content: {'✅ Yes' if message.content else '❌ No'}")
        
        # Try to react to show we can interact
        try:
            await message.add_reaction("👍")
            print(f"   Can add reactions: ✅ Yes")
        except:
            print(f"   Can add reactions: ❌ No")
        
        print()

async def main():
    """Run the permission test bot."""
    print("🤖 Discord Permission Checker")
    print("=" * 40)
    
    # Check if token exists
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN not found in environment variables!")
        return
    
    bot = PermissionTestBot()
    
    try:
        await bot.start(token)
    except discord.LoginFailure:
        print("❌ Invalid bot token! Check your DISCORD_TOKEN.")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✋ Test stopped by user.")