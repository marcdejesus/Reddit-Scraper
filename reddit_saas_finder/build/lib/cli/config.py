"""CLI for configuration management."""
import typer
from rich.console import Console
from rich.syntax import Syntax
import yaml
from utils.config import ConfigManager

app = typer.Typer(help="Manage application configuration.")
console = Console()
config_manager = ConfigManager()

@app.command()
def show():
    """
    Displays the contents of all loaded YAML configuration files.
    """
    raw_main, raw_subreddits = config_manager.get_raw_config_text()

    console.print("\n[bold cyan]Note: Configuration is loaded from within the installed package.[/bold cyan]")
    console.print("[cyan]To make changes, you may need to reinstall the package after editing the source files.[/cyan]")

    console.print("\n[bold green]--- Main Configuration (default.yaml) ---[/bold green]")
    if raw_main:
        console.print(Syntax(raw_main, "yaml", theme="solarized-dark", line_numbers=True))
    else:
        console.print(f"[yellow]Main configuration could not be loaded.[/yellow]")

    console.print("\n[bold green]--- Subreddits Configuration (subreddits.yaml) ---[/bold green]")
    if raw_subreddits:
        console.print(Syntax(raw_subreddits, "yaml", theme="solarized-dark", line_numbers=True))
    else:
        console.print(f"[yellow]Subreddits configuration could not be loaded.[/yellow]")

if __name__ == "__main__":
    app() 