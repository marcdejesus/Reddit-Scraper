import typer
from reddit_saas_finder.src.data.database import initialize_database
from reddit_saas_finder.src.data.reddit_client import RedditClient
from reddit_saas_finder.src.cli.processor import process_pain_points
from reddit_saas_finder.src.cli.opportunities import generate_and_score_opportunities
from reddit_saas_finder.src.cli.visualization import display_opportunities_table, display_category_distribution
from rich import print

app = typer.Typer()

@app.command()
def init():
    """Initializes the Reddit SaaS Finder."""
    print("Initializing Reddit SaaS Finder...")

@app.command()
def scrape(
    subreddit: str = typer.Option("entrepreneur", "--subreddit", "-s", help="The subreddit to scrape."),
    limit: int = typer.Option(100, "--limit", "-l", help="The maximum number of posts to scrape."),
    time_filter: str = typer.Option("week", "--time", "-t", help="The time filter for scraping (e.g., 'day', 'week', 'month', 'year', 'all').")
):
    """Scrapes Reddit data from a specified subreddit."""
    print(f"[bold green]Starting scrape for r/{subreddit}...[/bold green]")
    try:
        client = RedditClient()
        posts, comments = client.scrape_subreddit(subreddit_name=subreddit, limit=limit, time_filter=time_filter)
        if posts or comments:
            client.save_to_database(posts, comments)
            print(f"[bold green]Successfully scraped and saved {len(posts)} posts and {len(comments)} comments.[/bold green]")
        else:
            print("[bold yellow]Scraping completed with no new data.[/bold yellow]")
    except Exception as e:
        print(f"[bold red]An error occurred during scraping: {e}[/bold red]")

@app.command()
def process(
    analyze_pain_points: bool = typer.Option(False, "--analyze-pain-points", help="Run the pain point detection and analysis pipeline."),
    advanced: bool = typer.Option(False, "--advanced", help="Use the advanced transformer-based NLP model for higher accuracy.")
):
    """Processes the NLP pipeline."""
    if analyze_pain_points:
        print("[bold green]Starting NLP processing for pain points...[/bold green]")
        try:
            process_pain_points(use_advanced_detector=advanced)
            print("[bold green]Pain point processing completed successfully.[/bold green]")
        except Exception as e:
            print(f"[bold red]An error occurred during NLP processing: {e}[/bold red]")
    else:
        print("[bold yellow]No processing task selected. Use --help for options.[/bold yellow]")


@app.command()
def opportunities(
    generate: bool = typer.Option(False, "--generate", help="Generate and score opportunities from the processed pain points.")
):
    """Generates and scores opportunities."""
    if generate:
        print("[bold green]Starting opportunity generation and scoring...[/bold green]")
        try:
            generate_and_score_opportunities()
            print("[bold green]Opportunity generation completed successfully.[/bold green]")
        except Exception as e:
            print(f"[bold red]An error occurred during opportunity generation: {e}[/bold red]")
    else:
        print("[bold yellow]No action selected for opportunities. Use --help for options.[/bold yellow]")


@app.command()
def show(
    table: bool = typer.Option(False, "--table", help="Display opportunities in a table."),
    categories: bool = typer.Option(False, "--categories", help="Display category distribution chart."),
    limit: int = typer.Option(20, "--limit", "-l", help="Limit the number of opportunities to display in the table.")
):
    """Shows different visualizations of the opportunities data."""
    if table:
        display_opportunities_table(limit)
    if categories:
        display_category_distribution()
    if not table and not categories:
        print("[bold yellow]Please specify a visualization to show. Use --help for options.[/bold yellow]")


@app.command()
def init_db():
    """Initializes the database."""
    initialize_database()

if __name__ == "__main__":
    app() 