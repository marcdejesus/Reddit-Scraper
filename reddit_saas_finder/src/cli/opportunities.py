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
    print("[bold blue]Fetching processed pain points...[/bold blue]")
    pain_points = get_pain_points()
    if not pain_points:
        print("[bold yellow]No pain points found to generate opportunities from. Please run the processing step first.[/bold yellow]")
        return
    
    print(f"Found {len(pain_points)} pain points. Starting opportunity scoring...")
    
    scorer = OpportunityScorer()
    opportunities = scorer.generate_opportunities(pain_points)
    
    if not opportunities:
        print("[bold yellow]Could not generate any opportunities from the available pain points.[/bold yellow]")
        return

    print(f"Generated {len(opportunities)} opportunities. Saving to database...")
    
    opportunities_to_save = [
        OpportunityDB(
            title=opp['title'],
            description=opp['description'],
            category=opp.get('category', 'general'),
            total_score=opp['total_score'],
            market_score=opp.get('market_score', 0),
            frequency_score=opp.get('frequency_score', 0),
            willingness_to_pay_score=opp.get('wtp_score', 0),
            pain_point_count=opp['pain_point_count'],
        ) for opp in opportunities
    ]
    
    save_opportunities(opportunities_to_save)
    print(f"[bold green]Successfully saved {len(opportunities_to_save)} opportunities.[/bold green]")


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