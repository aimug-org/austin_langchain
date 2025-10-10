#!/bin/bash

# Development setup script for Austin LangChain Discord Bot

set -e

echo "🚀 Setting up Austin LangChain Discord Bot development environment..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install Poetry first:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please ensure Docker Compose is installed."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
poetry install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys and configuration"
else
    echo "✅ .env file already exists"
fi

# Start development services
echo "🐳 Starting development services..."
docker compose -f docker-compose.dev.yml up -d postgres redis

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Initialize database
echo "🗄️  Initializing database..."
poetry run python -c "
import asyncio
from discord_bot.services.database import db_service, create_tables

async def init():
    await db_service.initialize()
    await create_tables()
    print('Database initialized successfully!')

asyncio.run(init())
"

# Run tests to verify setup
echo "🧪 Running tests to verify setup..."
poetry run pytest tests/ -v

echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Discord bot token and API keys"
echo "2. Run 'poetry run discord-bot run' to start the bot"
echo "3. Or use 'poetry run discord-bot --help' to see available commands"
echo ""
echo "Development services:"
echo "- PostgreSQL: localhost:5432 (discord_bot/dev_password)"
echo "- Redis: localhost:6379"
echo "- Adminer (DB GUI): http://localhost:8080"