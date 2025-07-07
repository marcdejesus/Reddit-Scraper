"""Handles all Reddit data collection."""
import typer
from rich import print
from reddit_saas_finder.src.data.reddit_client import RedditClient

app = typer.Typer()

@app.command()
def subreddit(
    subreddit: str = typer.Option("entrepreneur", "--name", "-n", help="The subreddit to scrape."),
    limit: int = typer.Option(100, "--limit", "-l", help="The maximum number of posts to scrape."),
    time_filter: str = typer.Option("week", "--time", "-t", help="The time filter for scraping (e.g., 'day', 'week', 'month', 'year', 'all').")
):
    """
    Scrapes a specific subreddit for posts and comments and saves them to the database.
    """
    try:
        client = RedditClient()
        client.scrape_subreddit(subreddit_name=subreddit, limit=limit, time_filter=time_filter)
        print(f"[bold green]Scraping task for r/{subreddit} completed.[/bold green]")
    except Exception as e:
        print(f"[bold red]An error occurred during scraping setup: {e}[/bold red]")
