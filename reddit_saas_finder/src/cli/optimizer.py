
import typer
from rich.console import Console
from utils.performance import PerformanceOptimizer, profile_cli_command, optimize_database_queries

app = typer.Typer(help="Commands for performance optimization.")
console = Console()

@app.command()
def profile(command: str = typer.Argument(..., help="The full CLI command to profile, enclosed in quotes.")):
    """
    Profiles a CLI command to identify performance bottlenecks.
    
    Example: reddit-finder optimize profile "scrape --subreddit SaaS --limit 100"
    """
    profile_cli_command(command)

@app.command()
def db_optimize():
    """
    Optimizes the database by creating indexes on frequently queried columns.
    """
    console.print("[bold cyan]Optimizing database...[/bold cyan]")
    optimize_database_queries()
    console.print("[bold green]Database optimization check complete.[/bold green]")

@app.command()
def cache_clear():
    """
    Clears all cached data, including NLP results and API responses.

    This is useful for forcing a re-processing of data or to free up disk space.
    """
    console.print("[bold cyan]Clearing NLP cache...[/bold cyan]")
    optimizer = PerformanceOptimizer()
    optimizer.clear_cache()

@app.command()
def batch_process(
    batch_size: int = typer.Option(100, "--batch-size", help="Number of items to process in a single batch.")
):
    """
    Processes unprocessed data in batches to optimize memory usage.

    This is useful for systems with limited RAM, as it avoids loading all
    unprocessed posts and comments into memory at once.
    """
    optimizer = PerformanceOptimizer()
    optimizer.batch_process_pain_points(batch_size=batch_size) 