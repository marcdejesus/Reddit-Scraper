
import typer
from rich.console import Console
from utils.performance import PerformanceOptimizer

app = typer.Typer(help="Commands for performance optimization.")
console = Console()

@app.command()
def cache_clear():
    """
    Clears the NLP cache.
    """
    console.print("[bold cyan]Clearing NLP cache...[/bold cyan]")
    optimizer = PerformanceOptimizer()
    optimizer.clear_cache()

@app.command()
def batch_process(
    batch_size: int = typer.Option(100, "--batch-size", help="Number of items to process in a single batch.")
):
    """
    Processes pain points in batches to manage memory usage.
    """
    optimizer = PerformanceOptimizer()
    optimizer.batch_process_pain_points(batch_size=batch_size) 