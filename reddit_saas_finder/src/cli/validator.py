
import typer
from rich.console import Console

from utils.validators import DataValidator
from data.database import get_db_connection
from utils.config import load_config

app = typer.Typer(help="Commands for data validation and quality checks.")
console = Console()

@app.command()
def data():
    """
    Validates the integrity and quality of the scraped data.
    """
    console.print("[bold cyan]Running data validation...[/bold cyan]")
    config = load_config()
    conn = get_db_connection()
    validator = DataValidator(conn)
    
    validator.validate_data(
        spam_threshold=config.get('validation', {}).get('spam_score_threshold', 1),
        min_post_length=config.get('validation', {}).get('min_post_length', 20),
        min_comment_length=config.get('validation', {}).get('min_comment_length', 10)
    )
    
    conn.close()
    console.print("[bold green]Data validation complete. Use 'validate report' to see the results.[/bold green]")

@app.command()
def report():
    """
    Displays the data quality report.
    """
    console.print("[bold cyan]Generating data quality report...[/bold cyan]")
    conn = get_db_connection()
    validator = DataValidator(conn)
    # The validator needs to be run first to have a report.
    # This CLI structure is a bit problematic. Let's run validation and then report.
    config = load_config()
    validator.validate_data(
        spam_threshold=config.get('validation', {}).get('spam_score_threshold', 1),
        min_post_length=config.get('validation', {}).get('min_post_length', 20),
        min_comment_length=config.get('validation', {}).get('min_comment_length', 10)
    )
    validator.generate_quality_report()
    conn.close() 