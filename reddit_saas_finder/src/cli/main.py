import typer
from rich.console import Console
from data.database import initialize_database, get_db_connection
from cli.scraper import app as scraper_app
from cli.processor import process
from cli.opportunities import opportunities_app
from cli.export import export, report
from cli import docs as docs_cli
from cli import config as config_cli
from cli import trends as trends_cli

# Main Typer app
app = typer.Typer(
    name="reddit-finder",
    help="A CLI tool to find SaaS opportunities on Reddit."
)
console = Console()

def export_opportunities_command(
    format: str = typer.Option("csv", "--format", "-f", help="Export format (csv, json)."),
    output: str = typer.Option(None, "--output", "-o", help="The name of the output file.")
):
    """Exports all opportunities to a file."""
    from utils.export import DataExporter
    from data.database import get_opportunities
    exporter = DataExporter(export_dir="exports")
    data_to_export = get_opportunities(limit=1000)
    exporter.export_data(data_to_export, 'opportunities', format, output)

# Add subcommands from other modules
app.add_typer(scraper_app, name="scrape")
app.command()(process)
app.command()(export)
app.command("export-opportunities")(export_opportunities_command)
app.command()(report)
app.add_typer(opportunities_app, name="opportunities")
app.add_typer(docs_cli.app, name="docs")
app.add_typer(config_cli.app, name="config")
app.add_typer(trends_cli.app, name="trends")


@app.callback()
def main_callback():
    """
    Initializes the database before running any command.
    """
    console.print("[bold cyan]Initializing application...[/bold cyan]")
    try:
        conn = get_db_connection()
        initialize_database(conn)
        conn.close()
        console.print("[bold green]Database initialized successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error during database initialization: {e}[/bold red]")

if __name__ == "__main__":
    app() 