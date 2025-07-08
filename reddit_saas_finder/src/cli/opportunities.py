"""Handles opportunity generation and scoring."""
import typer
from rich.console import Console
from src.ml.opportunity_scorer import OpportunityScorer
from src.data.database import get_pain_points, save_opportunities, Opportunity as OpportunityDB, get_opportunities
from rich.table import Table

opportunities_app = typer.Typer()
console = Console()

@opportunities_app.command()
def generate(
    min_pain_points: int = typer.Option(5, "--min-points", help="Minimum number of related pain points to be considered an opportunity."),
    min_score: float = typer.Option(0.5, "--min-score", help="Minimum sentiment score for a pain point to be included.")
):
    """
    Analyzes detected pain points to generate and score potential SaaS opportunities.
    """
    console.print("[bold green]Generating SaaS opportunities...[/bold green]")
    try:
        pain_points = get_pain_points()
        if not pain_points:
            console.print("[yellow]No pain points found to analyze. Run the 'process' command first.[/yellow]")
            return

        scorer = OpportunityScorer(pain_points, min_pain_points, min_score)
        opportunities = scorer.generate_opportunities()
        
        if not opportunities:
            console.print("[yellow]No new opportunities generated based on the current criteria.[/yellow]")
            return
            
        save_opportunities(opportunities)
        console.print(f"[bold green]Successfully generated and saved {len(opportunities)} new opportunities.[/bold green]")

    except Exception as e:
        console.print(f"[bold red]An error occurred during opportunity generation: {e}[/bold red]")

@opportunities_app.command()
def show():
    """
    Displays a table of all generated opportunities, sorted by score.

    This command retrieves all opportunities from the database and presents them
    in a formatted table, including their ID, Title, Category, and Total Score.
    """
    opportunities = get_opportunities()

    table = Table(title="Opportunities")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Title", style="green")
    table.add_column("Category", style="cyan")
    table.add_column("Score", style="magenta", justify="right")

    for opp in opportunities:
        table.add_row(
            str(opp.id),
            opp.title,
            opp.category,
            f"{opp.total_score:.2f}"
        )

    console.print(table)

if __name__ == "__main__":
    opportunities_app() 