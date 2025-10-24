"""Buttondown API service for newsletter publishing."""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import httpx
import json

from discord_bot.core.config import settings
from discord_bot.core.logging import get_logger
from discord_bot.models.newsletter_models import Newsletter, PublishStatus

logger = get_logger(__name__)


class ButtondownService:
    """Service for publishing newsletters via Buttondown API."""
    
    def __init__(self):
        self.base_url = settings.buttondown_base_url
        self.api_key = settings.buttondown_api_key
        self.client: Optional[httpx.AsyncClient] = None
    
    async def initialize(self):
        """Initialize the Buttondown service."""
        if not self.api_key:
            logger.warning("Buttondown API key not configured")
            return
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        
        logger.info("Buttondown service initialized")
    
    async def close(self):
        """Close the Buttondown service."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("Buttondown service closed")
    
    async def create_draft(
        self,
        subject: str,
        body: str,
        newsletter_id: Optional[str] = None,
        tags: List[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a newsletter draft in Buttondown.
        
        Args:
            subject: Email subject line
            body: Newsletter HTML content
            newsletter_id: Internal newsletter ID for tracking
            tags: List of tags for categorization
            metadata: Metadata for subscriber management and categorization.
                     Includes fields like:
                     - newsletter_type: daily/weekly/preview
                     - source: austin-langchain-discord-bot
                     - subscriber_category: newsletter-{type}
                     - content_source: discord-community
                     
        Returns:
            Draft data from Buttondown API or None if failed
        """
        if not self.client:
            await self.initialize()
        
        if not self.client or not self.api_key:
            logger.warning("Buttondown API not available, using fallback")
            return self._create_fallback_draft(subject, body)
        
        try:
            payload = {
                "subject": subject,
                "body": body,
                "status": "draft"
            }

            if tags:
                payload["tags"] = tags

            if metadata:
                payload["metadata"] = metadata
            
            response = await self.client.post("/emails", json=payload)
            
            if response.status_code == 201:
                draft_data = response.json()
                logger.info("Created Buttondown draft", extra={
                    "draft_id": draft_data.get("id"),
                    "subject": subject[:50]
                })
                return draft_data
            else:
                logger.error(f"Failed to create Buttondown draft: {response.status_code} - {response.text}")
                return self._create_fallback_draft(subject, body)
                
        except Exception as e:
            logger.error(f"Error creating Buttondown draft: {e}")
            return self._create_fallback_draft(subject, body)
    
    async def update_draft(
        self,
        draft_id: str,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        tags: List[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Update an existing newsletter draft."""
        if not self.client or not self.api_key:
            logger.warning("Buttondown API not available")
            return None
        
        try:
            payload = {}
            
            if subject:
                payload["subject"] = subject
            if body:
                payload["body"] = body
            if tags:
                payload["tags"] = tags
            if metadata:
                payload["metadata"] = metadata
            
            response = await self.client.patch(f"/emails/{draft_id}", json=payload)
            
            if response.status_code == 200:
                updated_data = response.json()
                logger.info("Updated Buttondown draft", extra={
                    "draft_id": draft_id
                })
                return updated_data
            else:
                logger.error(f"Failed to update Buttondown draft: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error updating Buttondown draft: {e}")
            return None
    
    async def publish_draft(
        self,
        draft_id: str,
        scheduled_time: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """Publish a newsletter draft."""
        if not self.client or not self.api_key:
            logger.warning("Buttondown API not available")
            return None
        
        try:
            payload = {"status": "scheduled" if scheduled_time else "sent"}
            
            if scheduled_time:
                payload["publish_date"] = scheduled_time.isoformat()
            
            response = await self.client.patch(f"/emails/{draft_id}", json=payload)
            
            if response.status_code == 200:
                published_data = response.json()
                logger.info("Published Buttondown newsletter", extra={
                    "draft_id": draft_id,
                    "scheduled": bool(scheduled_time)
                })
                return published_data
            else:
                logger.error(f"Failed to publish Buttondown draft: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error publishing Buttondown draft: {e}")
            return None
    
    async def get_draft_status(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a newsletter draft."""
        if not self.client or not self.api_key:
            return None
        
        try:
            response = await self.client.get(f"/emails/{draft_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get draft status: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting draft status: {e}")
            return None
    
    async def get_newsletter_analytics(self, email_id: str) -> Optional[Dict[str, Any]]:
        """Get analytics for a published newsletter."""
        if not self.client or not self.api_key:
            return None
        
        try:
            response = await self.client.get(f"/emails/{email_id}/analytics")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"No analytics available for email {email_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting newsletter analytics: {e}")
            return None
    
    async def list_newsletters(
        self,
        limit: int = 20,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List newsletters from Buttondown."""
        if not self.client or not self.api_key:
            return []
        
        try:
            params = {"limit": limit}
            if status:
                params["status"] = status
            
            response = await self.client.get("/emails", params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
            else:
                logger.error(f"Failed to list newsletters: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing newsletters: {e}")
            return []
    
    async def get_subscriber_count(self) -> int:
        """Get current subscriber count."""
        if not self.client or not self.api_key:
            return 0
        
        try:
            response = await self.client.get("/subscribers")
            
            if response.status_code == 200:
                data = response.json()
                return data.get("count", 0)
            else:
                logger.error(f"Failed to get subscriber count: {response.status_code}")
                return 0
                
        except Exception as e:
            logger.error(f"Error getting subscriber count: {e}")
            return 0
    
    async def create_newsletter_from_model(
        self,
        newsletter: Newsletter,
        publish_immediately: bool = False,
        scheduled_time: Optional[datetime] = None
    ) -> Optional[str]:
        """Create and optionally publish a newsletter from a Newsletter model."""
        if not newsletter.content_html:
            logger.error("Newsletter has no HTML content")
            return None
        
        # Prepare tags
        tags = ["austin-langchain", newsletter.newsletter_type.value]
        if newsletter.newsletter_type.value == "daily":
            tags.append("daily")
        elif newsletter.newsletter_type.value == "weekly":
            tags.append("weekly")
        
        # Prepare metadata for subscriber management
        # This metadata helps Buttondown manage subscriber preferences and filtering
        # subscriber_category allows subscribers to choose which newsletter types to receive
        metadata = {
            "newsletter_type": newsletter.newsletter_type.value,  # daily, weekly, etc.
            "source": "austin-langchain-discord-bot",  # identifies the sending system
            "newsletter_id": str(newsletter.id),  # links back to our internal record
            "generated_at": newsletter.created_at.isoformat() if newsletter.created_at else None,
            "subscriber_category": f"newsletter-{newsletter.newsletter_type.value}",  # used for subscriber filtering
            "content_source": "discord-community"  # indicates content originates from Discord discussions
        }
        
        # Create draft
        draft_data = await self.create_draft(
            subject=newsletter.title,
            body=newsletter.content_html,
            newsletter_id=str(newsletter.id),
            tags=tags,
            metadata=metadata
        )
        
        if not draft_data:
            return None
        
        draft_id = draft_data.get("id")
        
        # Publish if requested
        if publish_immediately or scheduled_time:
            publish_result = await self.publish_draft(draft_id, scheduled_time)
            if publish_result:
                logger.info("Newsletter published successfully", extra={
                    "newsletter_id": str(newsletter.id),
                    "buttondown_id": draft_id
                })
        
        return draft_id
    
    async def preview_newsletter(
        self,
        subject: str,
        body: str
    ) -> Optional[Dict[str, Any]]:
        """Generate a preview of the newsletter."""
        if not self.client or not self.api_key:
            return {
                "preview_url": None,
                "subject": subject,
                "estimated_length": len(body),
                "note": "Preview not available without Buttondown API"
            }
        
        try:
            # Buttondown doesn't have a dedicated preview endpoint,
            # so we'll create a draft and get its details
            preview_metadata = {
                "newsletter_type": "preview",
                "source": "austin-langchain-discord-bot",
                "subscriber_category": "newsletter-preview"
            }
            
            draft_data = await self.create_draft(
                subject=f"[PREVIEW] {subject}",
                body=body,
                tags=["preview"],
                metadata=preview_metadata
            )
            
            if draft_data:
                return {
                    "preview_url": draft_data.get("preview_url"),
                    "subject": subject,
                    "draft_id": draft_data.get("id"),
                    "created_at": draft_data.get("creation_date"),
                    "estimated_length": len(body)
                }
            
        except Exception as e:
            logger.error(f"Error creating newsletter preview: {e}")
        
        return None
    
    def _create_fallback_draft(self, subject: str, body: str) -> Dict[str, Any]:
        """Create fallback draft data when API is not available."""
        import uuid
        
        fallback_id = str(uuid.uuid4())
        
        return {
            "id": fallback_id,
            "subject": subject,
            "body": body,
            "status": "draft",
            "creation_date": datetime.now(timezone.utc).isoformat(),
            "preview_url": None,
            "fallback": True,
            "note": "This is a fallback draft. Buttondown API is not configured."
        }
    
    def _validate_html_content(self, html_content: str) -> bool:
        """Basic validation of HTML content."""
        if not html_content:
            return False
        
        # Check for basic HTML structure
        has_basic_tags = any(tag in html_content.lower() for tag in ["<p>", "<div>", "<h1>", "<h2>", "<h3>"])
        
        # Check for reasonable length
        has_reasonable_length = 100 <= len(html_content) <= 100000
        
        return has_basic_tags and has_reasonable_length
    
    def _format_newsletter_html(self, content: str) -> str:
        """Apply additional formatting for email delivery."""
        # Add email-specific CSS and formatting
        email_styles = """
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; }
            .newsletter-container { max-width: 600px; margin: 0 auto; }
            .header { text-align: center; padding: 20px 0; border-bottom: 2px solid #0066cc; }
            .section { margin: 20px 0; padding: 15px; }
            .footer { text-align: center; font-size: 12px; color: #666; margin-top: 30px; }
        </style>
        """
        
        # Wrap content in email-friendly structure
        if "<html>" not in content.lower():
            content = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                {email_styles}
            </head>
            <body>
                <div class="newsletter-container">
                    {content}
                </div>
            </body>
            </html>
            """
        
        return content
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of Buttondown service."""
        health = {
            "service": "buttondown",
            "status": "unknown",
            "api_key_configured": bool(self.api_key),
            "client_initialized": bool(self.client)
        }
        
        if not self.api_key:
            health["status"] = "disabled"
            health["note"] = "Buttondown API key not configured"
            return health
        
        if not self.client:
            try:
                await self.initialize()
            except Exception as e:
                health["status"] = "error"
                health["error"] = str(e)
                return health
        
        # Test API connection
        try:
            response = await self.client.get("/emails", params={"limit": 1})
            
            if response.status_code == 200:
                health["status"] = "healthy"
                
                # Get additional info
                subscriber_count = await self.get_subscriber_count()
                health["subscriber_count"] = subscriber_count
                
            else:
                health["status"] = "error"
                health["error"] = f"API returned {response.status_code}"
                
        except Exception as e:
            health["status"] = "error"
            health["error"] = str(e)
        
        return health


# Global Buttondown service instance
buttondown_service = ButtondownService()