"""Main application entry point."""

import asyncio
import signal
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from discord_bot.core.config import settings
from discord_bot.core.logging import setup_logging, get_logger
from discord_bot.services.database import db_service, create_tables
from discord_bot.services.discord_service import discord_service
from discord_bot.services.perplexity_service import perplexity_service
from discord_bot.services.model_router import model_router
from discord_bot.services.buttondown_service import buttondown_service
from discord_bot.services.scheduler_service import scheduler_service

# Setup logging first
setup_logging()
logger = get_logger(__name__)


class Application:
    """Main application class."""
    
    def __init__(self):
        self._shutdown_event = asyncio.Event()
        self._services_started = False
    
    async def startup(self) -> None:
        """Initialize all application services."""
        logger.info("Starting Austin LangChain Discord Bot", extra={
            "version": "0.1.0",
            "environment": settings.environment,
            "debug": settings.debug
        })
        
        try:
            # Initialize database
            logger.info("Initializing database connection")
            await db_service.initialize()
            
            # Create tables if they don't exist
            if settings.is_development or settings.testing:
                await create_tables()
            
            # Check database health
            if not await db_service.health_check():
                raise RuntimeError("Database health check failed")
            
            # Initialize external services
            logger.info("Initializing external services")
            await perplexity_service.initialize()
            await model_router.initialize()
            await buttondown_service.initialize()
            
            # Initialize Discord service
            logger.info("Initializing Discord service")
            await discord_service.initialize()
            
            # Initialize scheduler service
            logger.info("Initializing scheduler service")
            await scheduler_service.initialize()
            await scheduler_service.start()
            
            self._services_started = True
            logger.info("All services initialized successfully")
            
        except Exception as e:
            logger.error("Failed to start application services", extra={
                "error": str(e),
                "error_type": type(e).__name__
            })
            await self.shutdown()
            raise
    
    async def run(self) -> None:
        """Run the main application loop."""
        try:
            await self.startup()
            
            # Setup signal handlers
            self._setup_signal_handlers()
            
            # Start Discord bot (this blocks until bot stops)
            logger.info("Starting Discord bot...")
            await discord_service.start()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error("Application error", extra={
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self) -> None:
        """Gracefully shutdown all services."""
        if not self._services_started:
            return
        
        logger.info("Shutting down application")
        
        try:
            # Stop scheduler service
            if scheduler_service.is_running:
                logger.info("Stopping scheduler service")
                await scheduler_service.stop()
            
            # Stop Discord service
            if discord_service.is_running:
                logger.info("Stopping Discord service")
                await discord_service.stop()
            
            # Close external services
            logger.info("Closing external services")
            await buttondown_service.close()
            await model_router.close()
            await perplexity_service.close()
            
            # Close database connections
            logger.info("Closing database connections")
            await db_service.close()
            
            self._services_started = False
            logger.info("Application shutdown complete")
            
        except Exception as e:
            logger.error("Error during shutdown", extra={
                "error": str(e),
                "error_type": type(e).__name__
            })
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}")
            self._shutdown_event.set()
        
        # Only setup signal handlers on Unix systems
        if sys.platform != "win32":
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
    
    async def health_check(self) -> dict:
        """Check health of all services."""
        health_status = {
            "application": {"status": "healthy"},
            "services": {}
        }
        
        try:
            # Check database
            health_status["services"]["database"] = {
                "status": "healthy" if await db_service.health_check() else "unhealthy"
            }
            
            # Check external services
            health_status["services"]["perplexity"] = await perplexity_service.health_check()
            health_status["services"]["model_router"] = await model_router.health_check()
            health_status["services"]["buttondown"] = await buttondown_service.health_check()
            
            # Check Discord service
            health_status["services"]["discord"] = {
                "status": "healthy" if discord_service.is_running else "stopped"
            }
            
            # Check scheduler
            health_status["services"]["scheduler"] = {
                "status": "healthy" if scheduler_service.is_running else "stopped",
                **scheduler_service.get_scheduler_status()
            }
            
            # Overall status
            unhealthy_services = [
                name for name, status in health_status["services"].items()
                if status.get("status") not in ["healthy", "disabled"]
            ]
            
            if unhealthy_services:
                health_status["application"]["status"] = "degraded"
                health_status["application"]["issues"] = unhealthy_services
            
        except Exception as e:
            health_status["application"]["status"] = "error"
            health_status["application"]["error"] = str(e)
        
        return health_status


@asynccontextmanager
async def create_app() -> AsyncGenerator[Application, None]:
    """Create and manage application lifecycle."""
    app = Application()
    try:
        yield app
    finally:
        await app.shutdown()


async def main() -> None:
    """Main entry point."""
    try:
        async with create_app() as app:
            await app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error("Application failed", extra={
            "error": str(e),
            "error_type": type(e).__name__
        })
        sys.exit(1)


if __name__ == "__main__":
    # Check for required configuration
    if not settings.discord_token:
        logger.error("DISCORD_TOKEN environment variable is required")
        sys.exit(1)
    
    if not settings.database_url:
        logger.error("DATABASE_URL environment variable is required")
        sys.exit(1)
    
    # Run the application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        sys.exit(0)