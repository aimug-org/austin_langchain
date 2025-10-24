.PHONY: help install test clean run sync engagement newsletter-daily newsletter-weekly newsletter-monthly newsletter-draft verify-schedules show-top lint format

# Default Python path for the project
export PYTHONPATH := $(shell pwd)/src

# Help target - shows all available commands
help:
	@echo "AIMUG Discord Bot - Make Commands"
	@echo "=================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install              Install dependencies with poetry"
	@echo "  make db-init              Initialize database and run migrations"
	@echo "  make dev-setup            Full development environment setup"
	@echo ""
	@echo "Running the Bot:"
	@echo "  make run                  Start the Discord bot"
	@echo "  make run-bot              Alternative: Start the bot via run_bot.py"
	@echo ""
	@echo "Newsletter Generation:"
	@echo "  make newsletter-daily     Generate daily newsletter"
	@echo "  make newsletter-weekly    Generate weekly newsletter"
	@echo "  make newsletter-biweekly  Generate bi-weekly newsletter"
	@echo "  make newsletter-monthly   Generate monthly newsletter"
	@echo "  make newsletter-draft     Publish latest newsletter as Buttondown draft"
	@echo ""
	@echo "Data Management:"
	@echo "  make sync                 Sync Discord messages to database"
	@echo "  make engagement           Calculate engagement metrics"
	@echo "  make recalculate          Recalculate all engagement scores"
	@echo "  make show-top             Show top engaged discussions"
	@echo ""
	@echo "Validation & Scripts:"
	@echo "  make verify-schedules     Verify newsletter schedule configuration"
	@echo "  make display-newsletter   Display latest newsletter"
	@echo ""
	@echo "Testing:"
	@echo "  make test                 Run all tests"
	@echo "  make test-coverage        Run tests with coverage report"
	@echo "  make test-bot             Quick bot connectivity test"
	@echo "  make test-permissions     Test Discord permissions"
	@echo "  make test-workflow        Test newsletter workflow"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint                 Run linting (flake8)"
	@echo "  make format               Format code (black + isort)"
	@echo "  make typecheck            Run type checking (mypy)"
	@echo "  make quality              Run all quality checks"
	@echo ""
	@echo "Database:"
	@echo "  make db-start             Start PostgreSQL container"
	@echo "  make db-stop              Stop PostgreSQL container"
	@echo "  make db-shell             Open PostgreSQL shell"
	@echo "  make db-migrate           Create new migration"
	@echo "  make db-upgrade           Apply migrations"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean                Remove generated files and caches"
	@echo "  make clean-output         Remove generated newsletters"

# Installation and Setup
install:
	poetry install

db-init:
	poetry run alembic upgrade head
	@echo "✅ Database initialized and migrations applied"

dev-setup:
	@echo "Setting up development environment..."
	poetry install
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Waiting for database to be ready..."
	@sleep 5
	poetry run alembic upgrade head
	@echo "✅ Development environment ready!"

# Running the Bot
run:
	poetry run python -m discord_bot.main

run-bot:
	poetry run python run_bot.py

# Newsletter Generation
newsletter-daily:
	@echo "Generating daily newsletter..."
	poetry run python generate_newsletter.py daily

newsletter-weekly:
	@echo "Generating weekly newsletter..."
	poetry run python generate_newsletter.py weekly

newsletter-biweekly:
	@echo "Generating bi-weekly newsletter..."
	poetry run python generate_newsletter.py biweekly

newsletter-monthly:
	@echo "Generating monthly newsletter..."
	poetry run python generate_newsletter.py monthly

newsletter-draft:
	@echo "Publishing newsletter to Buttondown as draft..."
	poetry run python scripts/publish_newsletter_draft_only.py

newsletter-september:
	@echo "Generating September 2025 newsletter..."
	poetry run python generate_historical_newsletter.py 2025 9

newsletter-historical:
	@echo "Usage: make newsletter-historical YEAR=2025 MONTH=9"
	@if [ -z "$(YEAR)" ] || [ -z "$(MONTH)" ]; then \
		echo "Error: YEAR and MONTH required"; \
		echo "Example: make newsletter-historical YEAR=2025 MONTH=9"; \
		exit 1; \
	fi
	@echo "Generating $(YEAR)-$(MONTH) newsletter..."
	poetry run python generate_historical_newsletter.py $(YEAR) $(MONTH)

# Data Management
sync:
	@echo "Syncing Discord messages..."
	poetry run python scripts/sync_messages.py

engagement:
	@echo "Calculating engagement metrics..."
	poetry run python scripts/calculate_engagement.py

recalculate:
	@echo "Recalculating all engagement scores..."
	poetry run python scripts/recalculate_engagement.py

show-top:
	@echo "Showing top engaged discussions..."
	poetry run python scripts/show_top_messages.py

# Validation & Scripts
verify-schedules:
	poetry run python scripts/verify_schedules.py

display-newsletter:
	poetry run python scripts/display_newsletter.py

# Testing
test:
	poetry run pytest tests/ -v

test-coverage:
	poetry run pytest tests/ --cov=discord_bot --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/index.html"

test-bot:
	poetry run python tests/test_bot_quick.py

test-permissions:
	poetry run python tests/test_discord_permissions.py

test-workflow:
	poetry run python tests/test_workflow.py

test-all-channels:
	poetry run python tests/test_all_channels.py

# Code Quality
lint:
	poetry run flake8 src tests scripts --max-line-length=120 --exclude=__pycache__,.git,alembic

format:
	@echo "Formatting code with black..."
	poetry run black src tests scripts
	@echo "Sorting imports with isort..."
	poetry run isort src tests scripts
	@echo "✅ Code formatted"

typecheck:
	poetry run mypy src --ignore-missing-imports

quality: format lint typecheck
	@echo "✅ All quality checks passed"

# Database
db-start:
	docker-compose -f docker-compose.dev.yml up -d postgres
	@echo "⏳ Waiting for PostgreSQL to be ready..."
	@sleep 3
	@echo "✅ PostgreSQL started"

db-stop:
	docker-compose -f docker-compose.dev.yml stop postgres

db-shell:
	PGPASSWORD=dev_password psql -h localhost -p 5433 -U discord_bot -d austin_langchain_bot

db-migrate:
	@read -p "Enter migration message: " msg; \
	poetry run alembic revision --autogenerate -m "$$msg"

db-upgrade:
	poetry run alembic upgrade head

db-downgrade:
	poetry run alembic downgrade -1

# Cleanup
clean:
	@echo "Cleaning up generated files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage
	@echo "✅ Cleanup complete"

clean-output:
	@echo "⚠️  This will delete all generated newsletters in output/"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		find output -name "newsletter_*.md" -delete; \
		echo "✅ Generated newsletters deleted"; \
	else \
		echo "Cancelled"; \
	fi

# Docker operations
docker-build:
	docker-compose build

docker-up:
	docker-compose -f docker-compose.dev.yml up -d

docker-down:
	docker-compose -f docker-compose.dev.yml down

docker-logs:
	docker-compose -f docker-compose.dev.yml logs -f

docker-restart:
	docker-compose -f docker-compose.dev.yml restart

# Combined workflows
workflow-daily: sync engagement newsletter-daily newsletter-draft
	@echo "✅ Daily newsletter workflow complete"

workflow-weekly: sync engagement newsletter-weekly newsletter-draft
	@echo "✅ Weekly newsletter workflow complete"

workflow-monthly: sync engagement newsletter-monthly newsletter-draft
	@echo "✅ Monthly newsletter workflow complete"

# Development workflows
dev-start: db-start
	@echo "Starting development environment..."
	@sleep 2
	make run

dev-stop: db-stop
	@echo "✅ Development environment stopped"

# Quick commands
quick-test: test-bot
	@echo "✅ Quick test complete"

quick-newsletter: newsletter-weekly
	@echo "✅ Quick newsletter generated"
