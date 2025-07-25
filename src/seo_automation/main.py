"""
Main CLI application entry point
"""
import asyncio
import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .config.settings import settings
from .utils.logging import setup_logging, get_logger
from .utils.vertex_ai_manager import vertex_ai_manager

# Setup logging first
setup_logging()
logger = get_logger(__name__)

app = typer.Typer(
    name="seo-automation",
    help="KloudPortal SEO Blog Commenting Automation with CrewAI",
    rich_markup_mode="rich"
)
console = Console()


@app.command()
def setup():
    """Initial setup and configuration validation."""
    rprint("[bold blue]🚀 KloudPortal SEO Automation Setup[/bold blue]")
    
    # Check environment configuration
    rprint("\n[yellow]📋 Configuration Check[/yellow]")
    
    config_table = Table(title="Configuration Status")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    config_table.add_column("Status", style="bold")
    
    # Check Google Cloud credentials
    creds_path = Path(settings.google_application_credentials)
    creds_status = "✅ Found" if creds_path.exists() else "❌ Missing"
    config_table.add_row(
        "Google Cloud Credentials",
        str(creds_path),
        creds_status
    )
    
    # Check project ID
    project_status = "✅ Set" if settings.google_cloud_project else "❌ Missing"
    config_table.add_row(
        "Google Cloud Project",
        settings.google_cloud_project or "Not set",
        project_status
    )
    
    # Check other settings
    config_table.add_row("Vertex AI Location", settings.vertex_ai_location, "✅ Set")
    config_table.add_row("Daily Budget", f"${settings.daily_budget_usd}", "✅ Set")
    config_table.add_row("Environment", settings.environment, "✅ Set")
    config_table.add_row("Log Level", settings.log_level, "✅ Set")
    
    console.print(config_table)
    
    # Test Vertex AI connection
    rprint("\n[yellow]🧪 Testing Vertex AI Connection[/yellow]")
    try:
        flash_model = vertex_ai_manager.get_flash_model()
        rprint("✅ Vertex AI Flash model initialized successfully")
        
        if vertex_ai_manager.check_daily_budget():
            rprint("✅ Daily budget check passed")
        else:
            rprint("⚠️  Daily budget exceeded")
            
    except Exception as e:
        rprint(f"❌ Vertex AI connection failed: {e}")
        logger.error("vertex_ai_connection_test_failed", error=str(e))
    
    rprint("\n[green]✨ Setup check complete![/green]")


@app.command()
def cost_report():
    """Display current cost usage report."""
    rprint("[bold blue]💰 Cost Usage Report[/bold blue]")
    
    report = vertex_ai_manager.get_usage_report()
    
    cost_table = Table(title=f"Daily Cost Report - {report['date']}")
    cost_table.add_column("Metric", style="cyan")
    cost_table.add_column("Value", style="green")
    
    cost_table.add_row("Daily Budget", f"${report['daily_budget']:.2f}")
    cost_table.add_row("Current Usage", f"${report['current_usage']:.4f}")
    cost_table.add_row("Remaining Budget", f"${report['remaining_budget']:.4f}")
    cost_table.add_row("Usage Percentage", f"{report['usage_percentage']:.1f}%")
    
    # Status indicators
    if report['budget_exceeded']:
        cost_table.add_row("Status", "❌ Budget Exceeded", style="bold red")
    elif report['alert_threshold_reached']:
        cost_table.add_row("Status", "⚠️  Approaching Limit", style="bold yellow")
    else:
        cost_table.add_row("Status", "✅ Within Budget", style="bold green")
    
    console.print(cost_table)
    
    # Available models
    rprint(f"\n[dim]Available models: {', '.join(report['available_models'])}[/dim]")


@app.command()
def test_model(
    model_type: str = typer.Option("flash", help="Model type: flash or pro"),
    prompt: str = typer.Option("Hello, this is a test", help="Test prompt")
):
    """Test Vertex AI model with a simple prompt."""
    rprint(f"[bold blue]🧪 Testing {model_type} model[/bold blue]")
    
    try:
        if model_type == "flash":
            model = vertex_ai_manager.get_flash_model()
        elif model_type == "pro":
            model = vertex_ai_manager.get_pro_model()
        else:
            rprint("❌ Invalid model type. Use 'flash' or 'pro'")
            return
        
        rprint(f"[yellow]Prompt:[/yellow] {prompt}")
        rprint("[yellow]Generating response...[/yellow]")
        
        # This is synchronous for simplicity in CLI
        response = model.invoke(prompt)
        
        rprint(f"[green]Response:[/green] {response.content}")
        
        # Estimate cost (rough approximation)
        input_tokens = len(prompt.split()) * 1.3
        output_tokens = len(response.content.split()) * 1.3
        
        model_name = "gemini-1.5-flash-001" if model_type == "flash" else "gemini-1.5-pro-001"
        cost = vertex_ai_manager.track_usage(
            model_name, 
            int(input_tokens), 
            int(output_tokens),
            "test"
        )
        
        rprint(f"[dim]Estimated cost: ${cost:.6f}[/dim]")
        
    except Exception as e:
        rprint(f"❌ Model test failed: {e}")
        logger.error("model_test_failed", model_type=model_type, error=str(e))


@app.command()
def info():
    """Display system information."""
    rprint("[bold blue]ℹ️  System Information[/bold blue]")
    
    info_table = Table()
    info_table.add_column("Component", style="cyan")
    info_table.add_column("Version/Status", style="green")
    
    info_table.add_row("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    info_table.add_row("Environment", settings.environment)
    info_table.add_row("Project Root", str(Path.cwd()))
    info_table.add_row("Logs Directory", "data/logs")
    info_table.add_row("Google Cloud Project", settings.google_cloud_project)
    info_table.add_row("Vertex AI Location", settings.vertex_ai_location)
    
    console.print(info_table)


if __name__ == "__main__":
    app()

