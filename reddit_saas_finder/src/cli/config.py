"""CLI for configuration management."""
import typer
from rich.console import Console
from rich.syntax import Syntax
import yaml
from utils.config import ConfigManager, CONFIG_PATH

app = typer.Typer(help="Manage application configuration.")
console = Console()
config_manager = ConfigManager()

@app.command()
def show():
    """
    Displays the contents of all loaded YAML configuration files.

    This command reads the raw text of `default.yaml` and `subreddits.yaml`
    and prints them to the console with syntax highlighting for readability.
    """
    raw_main, raw_subreddits = config_manager.get_raw_config_text()

    console.print("\n[bold green]--- Main Configuration (default.yaml) ---[/bold green]")
    if raw_main:
        console.print(Syntax(raw_main, "yaml", theme="solarized-dark", line_numbers=True))
    else:
        console.print(f"[yellow]Configuration file not found at {CONFIG_PATH}[/yellow]")

    console.print("\n[bold green]--- Subreddits Configuration (subreddits.yaml) ---[/bold green]")
    if raw_subreddits:
        console.print(Syntax(raw_subreddits, "yaml", theme="solarized-dark", line_numbers=True))
    else:
        console.print(f"[yellow]Subreddits configuration file not found.[/yellow]")

@app.command()
def edit():
    """
    Opens the main `default.yaml` configuration file in the default system editor.

    This provides a convenient way to quickly modify the main application settings.
    """
    console.print(f"Opening {CONFIG_PATH} in your default editor...")
    try:
        typer.launch(CONFIG_PATH)
    except Exception as e:
        console.print(f"[bold red]Failed to open editor: {e}[/bold red]")
        console.print("Please edit the file manually.")

if __name__ == "__main__":
    app() 