"""Handles opportunity generation and scoring."""
import typer
from rich import print
from reddit_saas_finder.src.ml.opportunity_scorer import OpportunityScorer
from reddit_saas_finder.src.data.database import get_pain_points, save_opportunities, Opportunity as OpportunityDB

app = typer.Typer()

def generate_and_score_opportunities():
    """
    Generates and scores opportunities from processed pain points.
    """
    print("[bold blue]Starting opportunity generation and scoring...[/bold blue]")
    try:
        scorer = OpportunityScorer()
        scorer.generate_opportunities()
        print("[bold green]Opportunity generation completed successfully.[/bold green]")
    except Exception as e:
        print(f"[bold red]An error occurred during opportunity generation: {e}[/bold red]")

@app.command()
def generate():
    """
    Generate and score opportunities from the processed pain points.
    """
    print("[bold green]Starting opportunity generation and scoring...[/bold green]")
    try:
        generate_and_score_opportunities()
        print("[bold green]Opportunity generation completed successfully.[/bold green]")
    except Exception as e:
        print(f"[bold red]An error occurred during opportunity generation: {e}[/bold red]")

if __name__ == "__main__":
    app() 