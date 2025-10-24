"""Command line interface for the Discord bot."""

import asyncio
import subprocess
import sys
import time
import os
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn

# Try to import optional dependencies
try:
    from sqlalchemy import select, func
    from discord_bot.core.config import settings
    from discord_bot.core.logging import setup_logging, get_logger
    from discord_bot.services.database import db_service, create_tables
    from discord_bot.services.discord_service import discord_service
    from discord_bot.services.perplexity_service import perplexity_service
    from discord_bot.services.model_router import model_router
    from discord_bot.services.buttondown_service import buttondown_service
    from discord_bot.services.scheduler_service import scheduler_service
    from discord_bot.services.newsletter_service import newsletter_service
    from discord_bot.models.discord_models import DiscordMessage, EngagementMetrics
    from discord_bot.models.newsletter_models import Newsletter, NewsletterType
    
    DEPENDENCIES_AVAILABLE = True
    setup_logging()
    logger = get_logger(__name__)
    
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    logger = None

# Setup CLI
app = typer.Typer(help="Austin LangChain Discord Bot CLI")
console = Console()


def async_command(f):
    """Decorator to run async commands."""
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def run_command(cmd: list, cwd: Optional[Path] = None, capture_output: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    if cwd is None:
        cwd = get_project_root()
    
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=capture_output,
        text=True,
        check=False
    )


def check_docker_available() -> bool:
    """Check if Docker is available."""
    try:
        result = run_command(["docker", "--version"])
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_docker_compose_available() -> bool:
    """Check if Docker Compose is available."""
    try:
        result = run_command(["docker-compose", "--version"])
        return result.returncode == 0
    except FileNotFoundError:
        return False


def get_container_status(service_name: str = None) -> dict:
    """Get status of Docker containers."""
    project_root = get_project_root()
    
    if service_name:
        cmd = ["docker-compose", "-f", "docker-compose.dev.yml", "ps", service_name]
    else:
        cmd = ["docker-compose", "-f", "docker-compose.dev.yml", "ps"]
    
    result = run_command(cmd, cwd=project_root)
    
    if result.returncode != 0:
        return {"status": "error", "message": result.stderr}
    
    # Parse output to determine status
    output_lines = result.stdout.strip().split('\n')
    if len(output_lines) <= 1:  # Header only
        return {"status": "stopped"}
    
    # Check if services are healthy/running
    running_services = []
    for line in output_lines[1:]:  # Skip header
        if "Up" in line:
            parts = line.split()
            if parts:
                running_services.append(parts[0])
    
    return {"status": "running" if running_services else "stopped", "services": running_services}


def start_docker_environment() -> bool:
    """Start Docker development environment."""
    project_root = get_project_root()
    
    console.print("🐳 Starting Docker development environment...", style="blue")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Starting containers...", total=None)
        
        # Start containers
        result = run_command(
            ["docker-compose", "-f", "docker-compose.dev.yml", "up", "-d"],
            cwd=project_root,
            capture_output=False
        )
        
        if result.returncode != 0:
            console.print("❌ Failed to start Docker environment", style="red")
            return False
        
        progress.update(task, description="Waiting for services to be healthy...")
        
        # Wait for services to be healthy
        max_attempts = 60  # 2 minutes
        attempt = 0
        
        while attempt < max_attempts:
            time.sleep(2)
            attempt += 1
            
            # Check if services are healthy
            health_result = run_command([
                "docker-compose", "-f", "docker-compose.dev.yml", "ps", "--filter", "health=healthy"
            ], cwd=project_root)
            
            if health_result.returncode == 0:
                healthy_lines = health_result.stdout.strip().split('\n')
                if len(healthy_lines) >= 3:  # Header + postgres + redis
                    break
        
        if attempt >= max_attempts:
            console.print("⚠️  Services started but may not be fully healthy", style="yellow")
            return True
    
    console.print("✅ Docker environment is ready", style="green")
    return True


def ensure_environment_ready() -> bool:
    """Ensure Docker environment is ready for operations."""
    try:
        # Check Docker availability
        if not check_docker_available():
            console.print("❌ Docker is not available. Please install Docker.", style="red")
            console.print("💡 Visit: https://docs.docker.com/get-docker/", style="blue")
            return False
        
        if not check_docker_compose_available():
            console.print("❌ Docker Compose is not available. Please install Docker Compose.", style="red")
            console.print("💡 Visit: https://docs.docker.com/compose/install/", style="blue")
            return False
        
        # Check container status
        status = get_container_status()
        
        if status["status"] == "error":
            console.print(f"❌ Error checking container status: {status.get('message', 'Unknown error')}", style="red")
            console.print("💡 Try running: docker-compose -f docker-compose.dev.yml ps", style="blue")
            return False
        
        if status["status"] == "stopped":
            console.print("📦 Docker environment is not running. Starting it now...", style="yellow")
            return start_docker_environment()
        
        if status["status"] == "running":
            console.print("✅ Docker environment is already running", style="green")
            return True
        
        return False
        
    except Exception as e:
        console.print(f"❌ Unexpected error checking environment: {e}", style="red")
        console.print("💡 Please check your Docker installation", style="blue")
        return False


def check_poetry_available() -> bool:
    """Check if Poetry is available."""
    try:
        result = run_command(["poetry", "--version"])
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_poetry() -> bool:
    """Install Poetry using the official installer."""
    console.print("📦 Installing Poetry...", style="blue")
    
    try:
        # Download and run the Poetry installer
        console.print("📥 Downloading Poetry installer...", style="blue")
        download_result = run_command([
            "curl", "-sSL", "https://install.python-poetry.org", "-o", "/tmp/install-poetry.py"
        ])
        
        if download_result.returncode != 0:
            console.print("❌ Failed to download Poetry installer", style="red")
            return False
        
        # Run the installer
        install_result = run_command([
            "python3", "/tmp/install-poetry.py"
        ], capture_output=False)
        
        if install_result.returncode != 0:
            console.print("❌ Failed to install Poetry", style="red")
            return False
        
        # Try to add Poetry to PATH for current session
        home_dir = os.path.expanduser("~")
        poetry_bin = os.path.join(home_dir, ".local", "bin")
        current_path = os.environ.get("PATH", "")
        if poetry_bin not in current_path:
            os.environ["PATH"] = f"{poetry_bin}:{current_path}"
        
        console.print("✅ Poetry installed successfully", style="green")
        
        # Clean up
        try:
            os.remove("/tmp/install-poetry.py")
        except:
            pass
        
        return True
        
    except Exception as e:
        console.print(f"❌ Error installing Poetry: {e}", style="red")
        console.print("💡 Try installing Poetry manually:", style="blue")
        console.print("   curl -sSL https://install.python-poetry.org | python3 -", style="blue")
        return False


def setup_dependencies() -> bool:
    """Install project dependencies using Poetry."""
    console.print("📚 Installing project dependencies...", style="blue")
    
    project_root = get_project_root()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Installing dependencies...", total=None)
        
        # Install dependencies
        result = run_command(
            ["poetry", "install"],
            cwd=project_root,
            capture_output=False
        )
        
        if result.returncode != 0:
            console.print("❌ Failed to install dependencies", style="red")
            return False
    
    console.print("✅ Dependencies installed successfully", style="green")
    return True


def check_env_file() -> bool:
    """Check if .env file exists and has basic configuration."""
    project_root = get_project_root()
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            console.print("📋 Copying .env.example to .env...", style="blue")
            try:
                import shutil
                shutil.copy2(env_example, env_file)
                console.print("✅ Created .env file from template", style="green")
                console.print("⚠️  Please edit .env with your API keys", style="yellow")
                return True
            except Exception as e:
                console.print(f"❌ Failed to create .env file: {e}", style="red")
                return False
        else:
            console.print("❌ No .env.example file found", style="red")
            return False
    
    console.print("✅ .env file exists", style="green")
    return True


def run_complete_setup() -> bool:
    """Run the complete environment setup."""
    console.print("🚀 Starting complete environment setup...", style="bold blue")
    
    # Check Poetry
    if not check_poetry_available():
        console.print("🔍 Poetry not found, installing...", style="yellow")
        if not install_poetry():
            return False
        
        # Check again after installation
        if not check_poetry_available():
            console.print("❌ Poetry installation failed or not in PATH", style="red")
            console.print("Please ensure Poetry is in your PATH and try again", style="yellow")
            return False
    else:
        console.print("✅ Poetry is available", style="green")
    
    # Setup dependencies
    if not setup_dependencies():
        return False
    
    # Check/create .env file
    if not check_env_file():
        return False
    
    # Start Docker environment
    if not ensure_environment_ready():
        return False
    
    console.print("🎉 Complete setup finished successfully!", style="bold green")
    console.print("💡 You can now run newsletter generation commands", style="blue")
    return True


def safe_import_check() -> tuple[bool, str]:
    """Safely check if we can import the required modules."""
    if DEPENDENCIES_AVAILABLE:
        return True, "All dependencies available"
    else:
        return False, "Required dependencies not installed (use --setup to install)"


@app.command()
@async_command
async def init_db():
    """Initialize the database with tables."""
    console.print("🗄️  Initializing database...", style="blue")
    
    try:
        await db_service.initialize()
        await create_tables()
        console.print("✅ Database initialized successfully!", style="green")
    except Exception as e:
        console.print(f"❌ Database initialization failed: {e}", style="red")
        raise typer.Exit(1)


@app.command()
@async_command
async def health_check():
    """Check the health of all services."""
    console.print("🏥 Running comprehensive health checks...", style="blue")
    
    # First check Docker environment
    console.print("🐳 Checking Docker environment...", style="blue")
    docker_status = get_container_status()
    
    # Initialize services
    try:
        await db_service.initialize()
        await perplexity_service.initialize()
        await model_router.initialize()
        await buttondown_service.initialize()
        await scheduler_service.initialize()
    except Exception as e:
        console.print(f"❌ Service initialization failed: {e}", style="red")
        raise typer.Exit(1)
    
    # Create health status tree
    tree = Tree("🏥 Service Health Status")
    
    # Docker environment health
    docker_branch = tree.add("🐳 Docker Environment")
    if docker_status["status"] == "running":
        docker_branch.add("Status: ✅ Running")
        if "services" in docker_status:
            for service in docker_status["services"]:
                docker_branch.add(f"  - {service}: ✅ Up")
    elif docker_status["status"] == "stopped":
        docker_branch.add("Status: ❌ Stopped")
        docker_branch.add("Tip: Run any command to auto-start the environment")
    else:
        docker_branch.add(f"Status: ❌ {docker_status.get('message', 'Unknown error')}")
    
    # Database health
    db_healthy = await db_service.health_check()
    db_branch = tree.add("🗄️  Database")
    db_branch.add(f"Status: {'✅ Healthy' if db_healthy else '❌ Unhealthy'}")
    
    # External services health
    services = {
        "🔍 Perplexity": perplexity_service.health_check(),
        "🤖 Model Router": model_router.health_check(),  
        "📧 Buttondown": buttondown_service.health_check()
    }
    
    all_healthy = db_healthy
    
    for service_name, health_coro in services.items():
        health = await health_coro
        service_branch = tree.add(service_name)
        
        status = health.get("status", "unknown")
        if status == "healthy":
            service_branch.add("Status: ✅ Healthy")
            service_branch.add(f"API Key: {'✅ Configured' if health.get('api_key_configured') else '⚠️  Not configured'}")
        elif status == "disabled":
            service_branch.add("Status: ⚠️  Disabled (no API key)")
            all_healthy = False
        else:
            service_branch.add(f"Status: ❌ {status.title()}")
            if "error" in health:
                service_branch.add(f"Error: {health['error']}")
            all_healthy = False
    
    # Discord service
    discord_branch = tree.add("💬 Discord Service")
    try:
        await discord_service.initialize()
        discord_branch.add("Status: ✅ Initialized")
        discord_branch.add(f"Channels: {len(discord_service.monitored_channels)} monitored")
    except Exception as e:
        discord_branch.add("Status: ❌ Failed to initialize")
        discord_branch.add(f"Error: {str(e)}")
        all_healthy = False
    
    # Scheduler service  
    scheduler_branch = tree.add("⏰ Scheduler Service")
    scheduler_status = scheduler_service.get_scheduler_status()
    scheduler_branch.add(f"Status: {'✅ Ready' if scheduler_status['scheduler_initialized'] else '❌ Not initialized'}")
    
    console.print(tree)
    console.print()
    
    if all_healthy:
        console.print("🎉 All critical services are healthy!", style="bold green")
    else:
        console.print("⚠️  Some services have issues - check configuration", style="bold yellow")


@app.command()
def start_env():
    """Start the Docker development environment."""
    console.print("🐳 Starting Docker environment...", style="blue")
    
    if not ensure_environment_ready():
        console.print("❌ Failed to start Docker environment", style="red")
        raise typer.Exit(1)
    else:
        console.print("✅ Docker environment is ready!", style="green")


@app.command()
def stop_env():
    """Stop the Docker development environment."""
    console.print("🛑 Stopping Docker environment...", style="blue")
    
    project_root = get_project_root()
    result = run_command(
        ["docker-compose", "-f", "docker-compose.dev.yml", "down"],
        cwd=project_root,
        capture_output=False
    )
    
    if result.returncode == 0:
        console.print("✅ Docker environment stopped", style="green")
    else:
        console.print("❌ Failed to stop Docker environment", style="red")
        raise typer.Exit(1)


@app.command()
def env_status():
    """Check Docker environment status."""
    console.print("🔍 Checking Docker environment status...", style="blue")
    
    if not check_docker_available():
        console.print("❌ Docker is not available", style="red")
        return
    
    if not check_docker_compose_available():
        console.print("❌ Docker Compose is not available", style="red")
        return
    
    status = get_container_status()
    
    if status["status"] == "running":
        console.print("✅ Docker environment is running", style="green")
        if "services" in status:
            console.print("Running services:", style="blue")
            for service in status["services"]:
                console.print(f"  - {service}", style="green")
    elif status["status"] == "stopped":
        console.print("❌ Docker environment is stopped", style="yellow")
        console.print("Run 'discord-bot start-env' to start it", style="blue")
    else:
        console.print(f"❌ Error: {status.get('message', 'Unknown error')}", style="red")


@app.command()
@async_command
async def sync_messages(
    hours: int = typer.Option(24, help="Hours of message history to sync"),
    force: bool = typer.Option(False, help="Force sync even if already done")
):
    """Sync recent messages from Discord channels."""
    console.print(f"📥 Syncing messages from last {hours} hours...", style="blue")
    
    try:
        await db_service.initialize()
        await discord_service.initialize()
        
        console.print("⚠️  Message sync requires Discord bot to be running", style="yellow")
        console.print("Use 'discord-bot run' to start the bot and sync messages automatically", style="blue")
        
    except Exception as e:
        console.print(f"❌ Message sync failed: {e}", style="red")
        raise typer.Exit(1)


@app.command()
@async_command
async def analyze_engagement(
    days: int = typer.Option(7, help="Number of days to analyze"),
    min_score: float = typer.Option(5.0, help="Minimum engagement score to display"),
    limit: int = typer.Option(10, help="Number of top discussions to show")
):
    """Analyze engagement metrics for discussions."""
    console.print(f"📊 Analyzing engagement for last {days} days...", style="blue")
    
    try:
        await db_service.initialize()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        async with db_service.get_session() as session:
            # Get top engaged messages
            result = await session.execute(
                select(DiscordMessage, EngagementMetrics)
                .join(EngagementMetrics)
                .where(DiscordMessage.created_at >= cutoff_date)
                .where(EngagementMetrics.engagement_score >= min_score)
                .order_by(EngagementMetrics.engagement_score.desc())
                .limit(limit)
            )
            
            messages_with_metrics = result.all()
            
            if not messages_with_metrics:
                console.print("No messages found matching criteria", style="yellow")
                return
            
            # Create table
            table = Table(title="Top Engaged Discussions")
            table.add_column("Score", style="cyan", width=8)
            table.add_column("Replies", style="green", width=8)
            table.add_column("Reactions", style="yellow", width=10)
            table.add_column("Participants", style="blue", width=12)
            table.add_column("Content", style="white", width=50)
            table.add_column("Date", style="dim", width=12)
            
            for message, metrics in messages_with_metrics:
                content = message.content[:47] + "..." if len(message.content) > 50 else message.content
                content = content.replace('\n', ' ')
                
                table.add_row(
                    f"{metrics.engagement_score:.1f}",
                    str(metrics.reply_count),
                    str(metrics.reaction_count),
                    str(metrics.discussion_participants),
                    content,
                    message.created_at.strftime("%m/%d/%Y")
                )
            
            console.print(table)
            
            # Summary stats
            total_messages = len(messages_with_metrics)
            avg_score = sum(m.engagement_score for _, m in messages_with_metrics) / total_messages
            
            console.print(Panel(
                f"📈 Analysis Summary\n"
                f"• {total_messages} high-engagement messages\n"
                f"• Average engagement score: {avg_score:.1f}\n"
                f"• Time period: {days} days",
                title="Summary",
                style="bold"
            ))
    
    except Exception as e:
        console.print(f"❌ Engagement analysis failed: {e}", style="red")
        raise typer.Exit(1)


@app.command()
@async_command
async def generate_newsletter(
    newsletter_type: str = typer.Option("daily", help="Newsletter type (daily/weekly)"),
    force: bool = typer.Option(False, help="Force generation even if one exists"),
    dry_run: bool = typer.Option(False, help="Simulate generation without creating"),
    auto_publish: bool = typer.Option(False, help="Automatically publish to Buttondown"),
    setup: bool = typer.Option(False, help="Run complete environment setup (Poetry, dependencies, Docker)")
):
    """Generate a newsletter."""
    console.print(f"📰 Generating {newsletter_type} newsletter...", style="blue")
    
    # Handle setup flag
    if setup:
        console.print("🔧 Running complete environment setup...", style="blue")
        if not run_complete_setup():
            console.print("❌ Setup failed. Cannot proceed with newsletter generation.", style="red")
            raise typer.Exit(1)
        
        console.print("✅ Setup complete! Proceeding with newsletter generation...", style="green")
    else:
        # Check if dependencies are available
        deps_available, deps_message = safe_import_check()
        if not deps_available:
            console.print("❌ Missing dependencies detected:", style="red")
            console.print(f"   {deps_message}", style="red")
            console.print("💡 Run with --setup flag to install all dependencies:", style="blue")
            console.print(f"   discord-bot generate-newsletter --newsletter-type {newsletter_type} --setup", style="blue")
            raise typer.Exit(1)
        
        # Ensure Docker environment is ready
        console.print("🔍 Checking environment requirements...", style="blue")
        if not ensure_environment_ready():
            console.print("❌ Environment setup failed. Cannot proceed with newsletter generation.", style="red")
            console.print("💡 Run with --setup flag for complete setup:", style="blue")
            console.print(f"   discord-bot generate-newsletter --newsletter-type {newsletter_type} --setup", style="blue")
            raise typer.Exit(1)
    
    if dry_run:
        console.print("🚀 This is a dry run - no newsletter will be created", style="yellow")
    
    try:
        # Validate newsletter type
        if newsletter_type not in ["daily", "weekly"]:
            console.print("❌ Newsletter type must be 'daily' or 'weekly'", style="red")
            raise typer.Exit(1)
        
        # Give containers a moment to fully start before connecting
        console.print("⏳ Allowing services to fully initialize...", style="blue")
        time.sleep(3)
        
        await db_service.initialize()
        await perplexity_service.initialize()
        await model_router.initialize()
        
        if auto_publish:
            await buttondown_service.initialize()
        
        # Import Newsletter here to avoid import issues
        from discord_bot.models.newsletter_models import Newsletter
        
        async with db_service.get_session() as session:
            # Check if newsletter already exists for today
            today = datetime.now().date()
            existing_result = await session.execute(
                select(Newsletter)
                .where(Newsletter.newsletter_type == newsletter_type)
                .where(func.date(Newsletter.created_at) == today)
            )
            existing_newsletter = existing_result.scalar_one_or_none()
            
            if existing_newsletter and not force:
                console.print(f"⚠️  {newsletter_type.title()} newsletter already exists for today", style="yellow")
                console.print("Use --force to regenerate", style="blue")
                return
            
            if dry_run:
                console.print(f"✅ Would generate {newsletter_type} newsletter", style="green")
                return
            
            # Generate newsletter
            with console.status(f"Generating {newsletter_type} newsletter..."):
                newsletter_type_enum = NewsletterType.DAILY if newsletter_type == "daily" else NewsletterType.WEEKLY
                newsletter = await newsletter_service.generate_newsletter(
                    newsletter_type=newsletter_type_enum,
                    force=force
                )
            
            if newsletter:
                console.print(f"✅ Newsletter generated successfully!", style="green")
                
                # Display newsletter info
                info_panel = Panel(
                    f"📰 {newsletter.title}\n"
                    f"📊 Word count: {newsletter.word_count or 0}\n"
                    f"⏱️  Read time: {newsletter.estimated_read_time or 0} minutes\n"
                    f"📅 Created: {newsletter.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                    f"🏷️  Status: {newsletter.status.value}",
                    title="Newsletter Details",
                    style="green"
                )
                console.print(info_panel)
                
                # Auto-publish if requested
                if auto_publish and newsletter.content_html:
                    with console.status("Publishing to Buttondown..."):
                        draft_id = await buttondown_service.create_newsletter_from_model(
                            newsletter=newsletter,
                            publish_immediately=False  # Create as draft for review
                        )
                    
                    if draft_id:
                        console.print(f"✅ Newsletter published to Buttondown as draft: {draft_id}", style="green")
                    else:
                        console.print("⚠️  Failed to publish to Buttondown", style="yellow")
            else:
                console.print("❌ Newsletter generation failed", style="red")
    
    except Exception as e:
        console.print(f"❌ Newsletter generation failed: {e}", style="red")
        raise typer.Exit(1)


@app.command()
@async_command
async def list_newsletters(
    days: int = typer.Option(30, help="Number of days to look back"),
    newsletter_type: Optional[str] = typer.Option(None, help="Filter by type (daily/weekly)"),
    show_stats: bool = typer.Option(False, help="Show generation statistics")
):
    """List recent newsletters."""
    console.print(f"📋 Listing newsletters from last {days} days...", style="blue")
    
    try:
        await db_service.initialize()
        
        # Get newsletters
        newsletters = await newsletter_service.get_recent_newsletters(
            days=days,
            newsletter_type=NewsletterType(newsletter_type) if newsletter_type else None
        )
        
        if not newsletters:
            console.print("No newsletters found", style="yellow")
            return
        
        # Create table
        table = Table(title="Recent Newsletters")
        table.add_column("Type", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Title", style="white", width=40)
        table.add_column("Created", style="dim")
        table.add_column("Words", style="blue")
        table.add_column("Read Time", style="magenta")
        
        for newsletter in newsletters:
            status_style = {
                "published": "green",
                "generated": "blue", 
                "failed": "red",
                "pending": "yellow",
                "generating": "cyan"
            }.get(newsletter.status.value, "white")
            
            table.add_row(
                newsletter.newsletter_type.value.title(),
                f"[{status_style}]{newsletter.status.value.title()}[/{status_style}]",
                newsletter.title[:37] + "..." if len(newsletter.title) > 40 else newsletter.title,
                newsletter.created_at.strftime("%m/%d %H:%M"),
                str(newsletter.word_count) if newsletter.word_count else "N/A",
                f"{newsletter.estimated_read_time}min" if newsletter.estimated_read_time else "N/A"
            )
        
        console.print(table)
        
        # Show statistics if requested
        if show_stats:
            stats = await newsletter_service.get_newsletter_statistics(days)
            
            stats_panel = Panel(
                f"📊 Generation Statistics ({days} days)\n"
                f"• Total newsletters: {stats['total_newsletters']}\n"
                f"• Success rate: {stats['success_rate']:.1%}\n"
                f"• Average word count: {stats['average_word_count']:.0f}\n"
                f"• Total words written: {stats['total_word_count']:,}",
                title="Statistics",
                style="bold"
            )
            console.print(stats_panel)
    
    except Exception as e:
        console.print(f"❌ Failed to list newsletters: {e}", style="red")
        raise typer.Exit(1)


@app.command()
@async_command
async def schedule_newsletter(
    newsletter_type: str = typer.Option(..., help="Newsletter type (daily/weekly)"),
    cron: str = typer.Option(..., help="Cron expression (e.g., '0 6 * * *')"),
    job_id: str = typer.Option(None, help="Custom job ID")
):
    """Schedule newsletter generation."""
    console.print(f"⏰ Scheduling {newsletter_type} newsletter...", style="blue")
    
    try:
        if newsletter_type not in ["daily", "weekly"]:
            console.print("❌ Newsletter type must be 'daily' or 'weekly'", style="red")
            raise typer.Exit(1)
        
        await scheduler_service.initialize()
        await scheduler_service.start()
        
        # Generate job ID if not provided
        if not job_id:
            job_id = f"custom_{newsletter_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Schedule newsletter
        newsletter_type_enum = NewsletterType.DAILY if newsletter_type == "daily" else NewsletterType.WEEKLY
        await scheduler_service.schedule_newsletter_generation(
            newsletter_type=newsletter_type_enum,
            cron_expression=cron,
            job_id=job_id
        )
        
        console.print(f"✅ Scheduled {newsletter_type} newsletter with job ID: {job_id}", style="green")
        
        # Show job status
        job_status = scheduler_service.get_job_status(job_id)
        if job_status:
            console.print(f"Next run: {job_status['next_run_time']}", style="blue")
        
    except Exception as e:
        console.print(f"❌ Failed to schedule newsletter: {e}", style="red")
        raise typer.Exit(1)


@app.command()
@async_command
async def list_jobs():
    """List scheduled jobs."""
    console.print("⏰ Listing scheduled jobs...", style="blue")
    
    try:
        await scheduler_service.initialize()
        
        jobs = scheduler_service.get_scheduled_jobs()
        
        if not jobs:
            console.print("No scheduled jobs found", style="yellow")
            return
        
        table = Table(title="Scheduled Jobs")
        table.add_column("Job ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Next Run", style="green")
        table.add_column("Trigger", style="dim")
        
        for job in jobs:
            table.add_row(
                job["id"],
                job["name"],
                job["next_run_time"] if job["next_run_time"] else "N/A",
                job["trigger"]
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Failed to list jobs: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def run():
    """Run the Discord bot (main application)."""
    console.print("🤖 Starting Austin LangChain Discord Bot...", style="blue")
    
    # First, ensure Docker environment is ready
    console.print("🔍 Checking environment requirements...", style="blue")
    if not ensure_environment_ready():
        console.print("❌ Environment setup failed. Cannot start Discord bot.", style="red")
        raise typer.Exit(1)
    
    # Import and run main application
    from discord_bot.main import main
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n👋 Bot stopped by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Bot failed to start: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def setup():
    """Run complete environment setup (Poetry, dependencies, Docker)."""
    console.print("🚀 Starting complete environment setup...", style="bold blue")
    
    if not run_complete_setup():
        console.print("❌ Setup failed", style="red")
        raise typer.Exit(1)
    
    console.print("✅ Setup complete! You can now run all commands.", style="bold green")
    console.print("💡 Try: python -m discord_bot.cli generate-newsletter --newsletter-type weekly", style="blue")


@app.command() 
def generate():
    """Generate newsletter (runs setup if needed)."""
    console.print("📰 Preparing to generate newsletter...", style="blue")
    
    # Check if dependencies are available
    deps_available, deps_message = safe_import_check()
    if not deps_available:
        console.print("🔧 Dependencies missing, running setup first...", style="yellow")
        if not run_complete_setup():
            console.print("❌ Setup failed", style="red")
            raise typer.Exit(1)
        console.print("✅ Setup complete! Now generating newsletter...", style="green")
        
        # After setup, we need to restart to load the dependencies
        console.print("🔄 Please re-run the command now that setup is complete:", style="blue")
        console.print("   python -m discord_bot.cli generate-newsletter --newsletter-type weekly", style="blue")
        return
    
    console.print("❌ This is a bootstrap command. Use generate-newsletter once dependencies are installed.", style="red")


@app.command()
def config():
    """Show current configuration."""
    console.print("⚙️  Current Configuration", style="blue")
    
    # Show safe configuration (no secrets)
    safe_config = settings.model_dump_safe()
    
    table = Table(title="Bot Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    
    # Group settings by category
    categories = {
        "Discord": ["discord_token", "discord_guild_id", "discord_channel_ids"],
        "Database": ["database_url", "database_pool_size"],
        "External APIs": ["langchain_api_key", "requesty_api_key", "perplexity_api_key", "buttondown_api_key"],
        "Newsletter": ["newsletter_schedule_daily", "newsletter_schedule_weekly", "timezone"],
        "General": ["environment", "debug", "log_level"]
    }
    
    for category, keys in categories.items():
        for key in keys:
            if key in safe_config:
                value = safe_config[key]
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                elif value is None:
                    value = "Not set"
                
                table.add_row(f"[bold]{category}[/bold] / {key.upper()}", str(value))
    
    console.print(table)


if __name__ == "__main__":
    app()