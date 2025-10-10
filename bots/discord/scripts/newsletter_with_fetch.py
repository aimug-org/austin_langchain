#!/usr/bin/env python3
"""
On-demand newsletter generation with Discord message fetching.
This script connects to Discord, fetches recent messages, and generates a newsletter.
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from discord_bot.services.newsletter_service import newsletter_service
from discord_bot.services.database import db_service
from discord_bot.services.perplexity_service import perplexity_service
from discord_bot.services.model_router import model_router
from discord_bot.models.newsletter_models import NewsletterType
from discord_bot.core.config import settings
from discord_bot.core.logging import setup_logging, get_logger

import discord
from discord.ext import commands

# Setup logging
setup_logging()
logger = get_logger(__name__)

class NewsletterBot(commands.Bot):
    """Temporary bot instance for fetching messages and generating newsletter."""
    
    def __init__(self):
        # Use minimal intents to avoid privileged intent requirements
        intents = discord.Intents.default()
        intents.guilds = True
        intents.guild_messages = True
        # Don't require message_content intent for this use case
        super().__init__(command_prefix='!', intents=intents)
        
        self.messages_fetched = 0
        self.newsletter_generated = False
        
    async def on_ready(self):
        """When bot connects, fetch messages and generate newsletter."""
        logger.info(f"Connected as {self.user} (ID: {self.user.id})")
        logger.info(f"Found {len(self.guilds)} guilds")
        
        try:
            await self.fetch_and_generate_newsletter()
        except Exception as e:
            logger.error(f"Newsletter generation failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.close()
    
    async def fetch_and_generate_newsletter(self):
        """Fetch recent messages and generate newsletter."""
        logger.info("Starting newsletter generation with message fetch...")
        
        # Initialize services
        await db_service.initialize()
        await perplexity_service.initialize()
        await model_router.initialize()
        
        # Fetch messages from last 7 days
        await self.fetch_recent_messages(days=7)
        
        if self.messages_fetched == 0:
            logger.warning("No messages fetched from Discord")
            print("⚠️  No messages found in Discord channels")
            print("   - Check bot permissions (Read Message History)")
            print("   - Verify guild has recent messages")
            print("   - Confirm bot is in the correct server")
            return
        
        logger.info(f"Fetched {self.messages_fetched} messages")
        print(f"✅ Fetched {self.messages_fetched} messages from Discord")
        
        # Generate newsletter
        print("🔄 Generating newsletter from collected data...")
        newsletter = await newsletter_service.generate_newsletter(
            newsletter_type=NewsletterType.WEEKLY,
            force=True
        )
        
        if newsletter:
            self.newsletter_generated = True
            print(f"\n🎉 Weekly newsletter generated successfully!")
            print(f"📰 Title: {newsletter.title}")
            print(f"📊 Status: {newsletter.status.value}")
            
            if newsletter.status.value == 'FAILED':
                print(f"❌ Error: {newsletter.error_message}")
            else:
                print(f"📝 Word count: {newsletter.word_count or 0}")
                print(f"⏱️  Read time: {newsletter.estimated_read_time or 0} minutes")
                print(f"📅 Created: {newsletter.created_at}")
                
                if newsletter.content_html:
                    print(f"\n📄 Content preview:")
                    print(newsletter.content_html[:400] + "...")
        else:
            print("❌ Newsletter generation returned None")
    
    async def fetch_recent_messages(self, days: int = 7):
        """Fetch messages from recent days."""
        from datetime import datetime, timedelta, timezone
        from discord_bot.models.discord_models import DiscordUser, DiscordGuild, DiscordChannel
        from discord_bot.models.discord_models import EngagementMetrics
        from discord_bot.services.engagement_service import engagement_service
        import uuid
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
        
        print(f"📥 Fetching messages from last {days} days...")
        print(f"🕐 Cutoff time: {cutoff_time}")
        
        async with db_service.get_session() as session:
            for guild in self.guilds:
                # Store guild info
                discord_guild = DiscordGuild(
                    guild_id=str(guild.id),
                    name=guild.name,
                    member_count=guild.member_count,
                    created_at=guild.created_at
                )
                session.merge(discord_guild)
                
                print(f"🏠 Processing guild: {guild.name}")
                
                text_channels = [ch for ch in guild.channels if isinstance(ch, discord.TextChannel)]
                print(f"📋 Found {len(text_channels)} text channels")
                
                for channel in text_channels:
                    try:
                        # Store channel info
                        discord_channel = DiscordChannel(
                            channel_id=str(channel.id),
                            guild_id=str(guild.id),
                            name=channel.name,
                            channel_type="text"
                        )
                        session.merge(discord_channel)
                        
                        channel_messages = 0
                        
                        async for message in channel.history(after=cutoff_time, limit=None):
                            # Store user info
                            discord_user = DiscordUser(
                                user_id=str(message.author.id),
                                username=message.author.name,
                                display_name=message.author.display_name,
                                is_bot=message.author.bot
                            )
                            session.merge(discord_user)
                            
                            # Store message
                            from discord_bot.models.discord_models import DiscordMessage, MessageType
                            discord_message = DiscordMessage(
                                id=uuid.uuid4(),
                                message_id=str(message.id),
                                guild_id=str(guild.id),
                                channel_id=str(channel.id),
                                author_id=str(message.author.id),
                                content=message.content,
                                clean_content=message.clean_content,
                                message_type=MessageType.DEFAULT,
                                created_at=message.created_at,
                                is_edited=False,
                                has_attachments=len(message.attachments) > 0,
                                has_embeds=len(message.embeds) > 0
                            )
                            session.add(discord_message)
                            
                            # Create basic engagement metrics
                            engagement = EngagementMetrics(
                                message_id=discord_message.id,
                                reply_count=0,  # Would need to count replies
                                reaction_count=len(message.reactions),
                                unique_reactors=sum([reaction.count for reaction in message.reactions]),
                                engagement_score=len(message.reactions) * 2,  # Simple scoring
                                trending_score=0.0,
                                discussion_participants=1,
                                sentiment_score=0.0,
                                toxicity_score=0.0
                            )
                            session.add(engagement)
                            
                            channel_messages += 1
                            self.messages_fetched += 1
                            
                            # Rate limiting
                            if self.messages_fetched % 50 == 0:
                                await session.commit()
                                await asyncio.sleep(0.5)
                        
                        if channel_messages > 0:
                            print(f"  📝 {channel.name}: {channel_messages} messages")
                        
                    except discord.Forbidden:
                        print(f"  ❌ No access to #{channel.name}")
                    except Exception as e:
                        print(f"  ⚠️  Error in #{channel.name}: {e}")
                
            # Final commit
            await session.commit()
        
        print(f"✅ Total messages fetched: {self.messages_fetched}")

async def main():
    """Main function to run newsletter generation with message fetch."""
    print("🤖 Starting on-demand newsletter generation...")
    print("🔄 This will:")
    print("   1. Connect to Discord")
    print("   2. Fetch messages from last 7 days")
    print("   3. Generate weekly newsletter")
    print("   4. Disconnect")
    print()
    
    bot = NewsletterBot()
    
    try:
        await bot.start(settings.discord_token)
    except Exception as e:
        logger.error(f"Bot failed to start: {e}")
        print(f"❌ Failed to connect to Discord: {e}")
        return False
    
    return bot.newsletter_generated

if __name__ == "__main__":
    result = asyncio.run(main())
    exit_code = 0 if result else 1
    print(f"\n🏁 Newsletter generation {'succeeded' if result else 'failed'}")
    exit(exit_code)