
import typer
from rich.console import Console

from utils.scheduler import TaskScheduler
from utils.config import ConfigManager

app = typer.Typer(help="Commands for scheduling scraping and processing tasks.")
console = Console()

@app.command()
def start(
    interval: int = typer.Option(None, "--interval", help="Interval in hours for running the scraper. Overrides config.")
):
    """
    Starts the background scheduler to run tasks at a specified interval.

    This command daemonizes a process that periodically runs the data scraping
    and processing pipeline. The interval can be set via the `--interval` option
    or configured in the `default.yaml` file.
    """
    config_manager = ConfigManager()
    config = config_manager.config
    scheduler_config = config.get('scheduler', {})
    
    interval_hours = interval if interval is not None else scheduler_config.get('interval_hours', 12)
    
    console.print(f"[bold cyan]Starting scheduler to run every {interval_hours} hours...[/bold cyan]")
    scheduler = TaskScheduler()
    scheduler.start(interval_hours=interval_hours)

@app.command()
def stop():
    """
    Stops the background scheduler if it is running.

    This command finds the process ID (PID) of the running scheduler
    and terminates it.
    """
    console.print("[bold cyan]Stopping scheduler...[/bold cyan]")
    scheduler = TaskScheduler()
    scheduler.stop()

@app.command()
def status():
    """
    Checks and reports the current status of the background scheduler.

    This will check if the scheduler process is currently running and
    report its status.
    """
    console.print("[bold cyan]Checking scheduler status...[/bold cyan]")
    scheduler = TaskScheduler()
    scheduler.get_status() 