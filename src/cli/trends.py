"""Handles CLI commands for trend analysis."""
import typer
from rich import print
from rich.table import Table
from rich.console import Console

from reddit_saas_finder.src.ml.trend_detector import TrendAnalyzer

app = typer.Typer(help="Analyze trends in opportunities and pain points.")
analyzer = TrendAnalyzer()
console = Console()

@app.command()
def analyze(days: int = typer.Option(30, "--days", "-d", help="Number of days to look back for trend analysis.")):
    """Analyze the overall trend of pain points."""
    trends = analyzer.analyze_opportunity_trends(days=days)
    if "error" in trends:
        print(f"[bold red]Error: {trends['error']}[/bold red]")
        return
    
    print(f"[bold green]Trend Analysis ({days} days):[/bold green] {trends['summary']}")
    
    table = Table(title="Daily Pain Point Mentions")
    table.add_column("Date", style="cyan")
    table.add_column("Count", style="magenta")

    if trends.get('daily_counts'):
        for date, count in trends['daily_counts'].items():
            table.add_row(str(date.date()), str(count))
        console.print(table)
    else:
        print("[yellow]No daily data to display.[/yellow]")


@app.command()
def seasonal():
    """Detect seasonal patterns in pain point mentions."""
    patterns = analyzer.detect_seasonal_patterns()
    if "error" in patterns:
        print(f"[bold red]Error: {patterns['error']}[/bold red]")
        return
        
    print(f"[bold green]Seasonal Patterns:[/bold green] {patterns['summary']}")
    
    table = Table(title="Monthly Pain Point Mentions")
    table.add_column("Month", style="cyan")
    table.add_column("Count", style="magenta")
    
    if patterns.get('monthly_counts'):
        # Sort months for display if possible (not implemented here for simplicity)
        for month, count in patterns['monthly_counts'].items():
            table.add_row(month, str(count))
        console.print(table)
    else:
        print("[yellow]No monthly data to display.[/yellow]")

@app.command()
def predict(id: int = typer.Option(..., "--id", help="The ID of the opportunity to predict growth for.")):
    """Predict the growth trend for a specific opportunity."""
    prediction = analyzer.predict_opportunity_growth(opportunity_id=id)
    print(f"[bold green]Growth Prediction for Opportunity {prediction['opportunity_id']}:[/bold green]")
    print(f"  - Predicted Growth Probability: [bold cyan]{prediction['growth_prediction']:.2f}[/bold cyan]")
    print(f"  - Status: [yellow]{prediction['status']}[/yellow]") 