"""Handles trend detection and analysis."""

import typer
from rich.console import Console
from rich.table import Table

from data.database import get_db_connection
from ml.trend_detector import TrendDetector

console = Console()

app = typer.Typer(help="Commands for trend detection and analysis.")

@app.command()
def analyze(days: int = typer.Option(60, "--days", help="Number of days to analyze for trends.")):
    """Analyze opportunity trends over the last N days."""
    console.print(f"[bold green]Analyzing opportunity trends over the last {days} days...[/bold green]")
    conn = get_db_connection()
    detector = TrendDetector(conn)
    results = detector.analyze_opportunity_trends(days=days)
    conn.close()

    if not results:
        console.print("[yellow]No opportunity trends found.[/yellow]")
        return

    table = Table(title=f"Opportunity Trends (Last {days} Days)")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Total Score", style="green")
    table.add_column("Trend", style="yellow")

    for res in results:
        table.add_row(str(res['id']), res['title'], f"{res['total_score']:.2f}", res['trend'])
    
    console.print(table)

@app.command()
def seasonal():
    """Detect seasonal patterns in pain point frequency."""
    console.print("[bold green]Detecting seasonal patterns...[/bold green]")
    conn = get_db_connection()
    detector = TrendDetector(conn)
    patterns = detector.detect_seasonal_patterns()
    conn.close()

    if not patterns:
        console.print("[yellow]No seasonal patterns detected.[/yellow]")
        return

    table = Table(title="Seasonal Pain Point Patterns (by Month)")
    table.add_column("Month", style="cyan")
    table.add_column("Pain Point Count", style="magenta")

    for month, count in patterns.items():
        table.add_row(month, str(count))
        
    console.print(table)

@app.command()
def predict(opportunity_id: int = typer.Option(..., "--id", help="The ID of the opportunity to predict.")):
    """Predict growth for a specific opportunity."""
    console.print(f"[bold green]Predicting growth for opportunity ID: {opportunity_id}...[/bold green]")
    conn = get_db_connection()
    detector = TrendDetector(conn)
    growth_prob = detector.predict_opportunity_growth(opportunity_id)
    conn.close()

    console.print(f"Predicted probability of growth: [bold yellow]{growth_prob:.2f}[/bold yellow] (0-1 scale)")
    if growth_prob > 0.7:
        console.print("[cyan]This opportunity shows strong signs of growth.[/cyan]")
    elif growth_prob > 0.5:
        console.print("[cyan]This opportunity shows moderate signs of growth.[/cyan]")
    else:
        console.print("[cyan]This opportunity shows stable or declining interest.[/cyan]") 