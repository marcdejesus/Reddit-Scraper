import typer
from rich import print
from data.database import initialize_database
from cli import (
    opportunities, 
    visualization, 
    config as config_cli,
    keywords as keywords_cli,
    export as export_cli,
    trends as trends_cli,
    validator as validator_cli,
    optimizer as optimizer_cli,
    scheduler as scheduler_cli,
    docs as docs_cli
)
from cli.scraper import scrape
from cli.processor import process
from cli.export import export, report
from data.database import get_db_connection

app = typer.Typer(help="Reddit SaaS Opportunity Finder CLI")

# Register the scrape command directly
app.command()(scrape)
app.command()(process)
app.command()(export)
app.command()(report)

app.add_typer(opportunities.app, name="opportunities", help="Generate and score opportunities.")
app.add_typer(visualization.app, name="show", help="Display data in tables and charts.")
app.add_typer(config_cli.app, name="config", help="Manage application configuration.")
app.add_typer(keywords_cli.app, name="keywords", help="Manage custom keywords for NLP processing.")
app.add_typer(trends_cli.app, name="trends", help="Analyze trends in opportunities and pain points.")
app.add_typer(validator_cli.app, name="validate", help="Validate data quality.")
app.add_typer(optimizer_cli.app, name="optimize", help="Optimize performance.")
app.add_typer(scheduler_cli.app, name="schedule", help="Schedule background tasks.")
app.add_typer(docs_cli.app, name="docs", help="Generate API documentation.")

@app.command()
def init_db():
    """
    Initializes the database with the required schema.
    """
    print("[bold green]Initializing database...[/bold green]")
    try:
        initialize_database()
        print("[bold green]Database initialized successfully.[/bold green]")
    except Exception as e:
        print(f"[bold red]An error occurred during database initialization: {e}[/bold red]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app() 