"""Database service for managing connections and sessions."""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    AsyncEngine, 
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool
from discord_bot.core.config import settings
from discord_bot.core.logging import get_logger
from discord_bot.models.base import Base

logger = get_logger(__name__)


class DatabaseService:
    """Database service for managing connections and sessions."""
    
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize database connection and session factory."""
        if self._initialized:
            return
        
        logger.info("Initializing database connection", extra={
            "database_url": settings.database_url.split("@")[-1],  # Hide credentials
            "pool_size": settings.database_pool_size,
            "max_overflow": settings.database_max_overflow
        })
        
        # Create async engine
        self._engine = create_async_engine(
            settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_pre_ping=True,
            echo=settings.debug,
            # Use NullPool for testing to avoid connection issues
            poolclass=NullPool if settings.testing else None,
        )
        
        # Create session factory
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        self._initialized = True
        logger.info("Database connection initialized successfully")
    
    async def create_tables(self) -> None:
        """Create all database tables."""
        if not self._engine:
            await self.initialize()
        
        logger.info("Creating database tables")
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    
    async def drop_tables(self) -> None:
        """Drop all database tables (use with caution)."""
        if not self._engine:
            await self.initialize()
        
        logger.warning("Dropping all database tables")
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("All database tables dropped")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session with automatic cleanup."""
        if not self._session_factory:
            await self.initialize()
        
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error("Database session error", extra={
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> bool:
        """Check database health."""
        try:
            if not self._engine:
                await self.initialize()

            from sqlalchemy import text
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))

            logger.debug("Database health check passed")
            return True
        except Exception as e:
            logger.error("Database health check failed", extra={
                "error": str(e),
                "error_type": type(e).__name__
            })
            return False
    
    async def close(self) -> None:
        """Close database connections."""
        if self._engine:
            logger.info("Closing database connections")
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            self._initialized = False
            logger.info("Database connections closed")
    
    @property
    def is_initialized(self) -> bool:
        """Check if database service is initialized."""
        return self._initialized
    
    @property
    def engine(self) -> Optional[AsyncEngine]:
        """Get the database engine."""
        return self._engine


# Global database service instance
db_service = DatabaseService()


# Convenience functions
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session (convenience function)."""
    async with db_service.get_session() as session:
        yield session


async def init_db() -> None:
    """Initialize database (convenience function)."""
    await db_service.initialize()


async def create_tables() -> None:
    """Create database tables (convenience function)."""
    await db_service.create_tables()


async def close_db() -> None:
    """Close database connections (convenience function)."""
    await db_service.close()