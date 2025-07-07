import typer
from rich import print
from data.database import initialize_database
from cli import (
    scraper, 
    processor, 
    opportunities, 
    visualization, 
    config as config_cli,
    keywords as keywords_cli,
    export as export_cli,
    trends as trends_cli
)

app = typer.Typer(help="Reddit SaaS Opportunity Finder CLI")

app.add_typer(scraper.app, name="scrape", help="Scrape data from Reddit subreddits.")
app.add_typer(processor.app, name="process", help="Process scraped data for pain points.")
app.add_typer(opportunities.app, name="opportunities", help="Generate and score opportunities.")
app.add_typer(visualization.app, name="show", help="Display data in tables and charts.")
app.add_typer(config_cli.app, name="config", help="Manage application configuration.")
app.add_typer(keywords_cli.app, name="keywords", help="Manage custom keywords for NLP processing.")
app.add_typer(export_cli.app, name="export", help="Export data and generate reports.")
app.add_typer(trends_cli.app, name="trends", help="Analyze trends in opportunities and pain points.")

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

if __name__ == "__main__":
    app() 