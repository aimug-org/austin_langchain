#!/usr/bin/env python3
"""
Test Discord bot message access with and without content intent.
"""

import asyncio
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

# Load environment variables
load_dotenv()

class MessageAccessTestBot(commands.Bot):
    """Test bot to check message access capabilities."""
    
    def __init__(self, use_message_content=True):
        # Configure intents
        intents = discord.Intents.default()
        intents.guilds = True
        intents.guild_messages = True
        
        if use_message_content:
            intents.message_content = True
            print("🔧 Attempting to use MESSAGE CONTENT intent (privileged)")
        else:
            print("🔧 Running WITHOUT message content intent")
        
        super().__init__(command_prefix='!', intents=intents)
        self.use_message_content = use_message_content
        
    async def on_ready(self):
        """Called when bot is ready."""
        print(f"\n✅ Bot connected as: {self.user}")
        print(f"🏠 Guild: {self.guilds[0].name if self.guilds else 'None'}")
        
        if not self.guilds:
            print("❌ Bot is not in any guilds!")
            await self.close()
            return
        
        guild = self.guilds[0]
        
        # Find a channel with recent messages
        test_channel = None
        for channel in guild.text_channels:
            if channel.permissions_for(guild.get_member(self.user.id)).read_messages:
                test_channel = channel
                break
        
        if not test_channel:
            print("❌ No accessible channels found!")
            await self.close()
            return
        
        print(f"\n📋 Testing message access in #{test_channel.name}")
        print("=" * 50)
        
        # Fetch recent messages
        messages_found = 0
        async for message in test_channel.history(limit=5):
            messages_found += 1
            print(f"\n📨 Message {messages_found}:")
            print(f"   Author: {message.author.name}")
            print(f"   Created: {message.created_at}")
            print(f"   Message ID: {message.id}")
            
            if self.use_message_content:
                if message.content:
                    print(f"   Content: {message.content[:100]}{'...' if len(message.content) > 100 else ''}")
                else:
                    print(f"   Content: [Empty or unable to read]")
            else:
                print(f"   Content: [Not available - message_content intent not enabled]")
            
            print(f"   Has attachments: {len(message.attachments) > 0}")
            print(f"   Has embeds: {len(message.embeds) > 0}")
            print(f"   Reactions: {len(message.reactions)}")
        
        if messages_found == 0:
            print("   📭 No messages found in this channel")
        
        print("\n" + "=" * 50)
        print(f"📊 Summary: Found {messages_found} messages")
        
        if self.use_message_content:
            print("\n✅ MESSAGE CONTENT INTENT is enabled")
            print("   The bot CAN read message text content")
        else:
            print("\n⚠️  MESSAGE CONTENT INTENT is not enabled")
            print("   The bot CANNOT read message text content")
            print("   But it CAN still see message metadata (author, timestamp, etc.)")
        
        # Test live message monitoring
        print("\n🔍 Testing live message monitoring...")
        print("   Waiting 10 seconds for new messages...")
        print("   Send a test message to see if the bot can detect it.")
        
        # Set up a 10-second timeout
        self.test_complete = False
        asyncio.create_task(self.timeout_test())
        
    async def timeout_test(self):
        """Stop the test after 10 seconds."""
        await asyncio.sleep(10)
        if not self.test_complete:
            print("\n⏱️  Test timeout - no new messages detected")
            self.test_complete = True
            await self.close()
    
    async def on_message(self, message):
        """Handle new messages."""
        # Skip bot messages
        if message.author.bot:
            return
        
        if not self.test_complete:
            print(f"\n🆕 New message detected!")
            print(f"   Channel: #{message.channel.name}")
            print(f"   Author: {message.author.name}")
            
            if self.use_message_content and message.content:
                print(f"   Content: {message.content[:100]}{'...' if len(message.content) > 100 else ''}")
            else:
                print(f"   Content: [Cannot read - {'intent not enabled' if not self.use_message_content else 'empty'}]")
            
            self.test_complete = True
            print("\n✅ Message monitoring test complete!")
            await self.close()

async def main():
    """Run the message access test."""
    print("🤖 Discord Message Access Test")
    print("=" * 40)
    
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN not found!")
        return
    
    # First try with message content intent
    print("\n📝 Test 1: WITH message content intent")
    print("-" * 40)
    
    bot = MessageAccessTestBot(use_message_content=True)
    try:
        await bot.start(token)
    except discord.errors.PrivilegedIntentsRequired:
        print("❌ MESSAGE CONTENT INTENT not enabled in Discord Developer Portal!")
        print("\n📝 Test 2: WITHOUT message content intent")
        print("-" * 40)
        
        # Try without message content intent
        bot2 = MessageAccessTestBot(use_message_content=False)
        try:
            await bot2.start(token)
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())