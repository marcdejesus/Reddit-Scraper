"""Handles all Reddit data collection."""
import typer
from rich import print
from src.data.reddit_client import RedditClient
from typing_extensions import Annotated

# This file will now export the command function directly, 
# instead of a Typer app. This allows it to be added as a top-level command.

def scrape(
    subreddit: Annotated[str, typer.Option("--subreddit", "-s", help="The subreddit to scrape.")] = "entrepreneur",
    limit: Annotated[int, typer.Option("--limit", "-l", help="The maximum number of posts to scrape.")] = 100,
    time_filter: Annotated[str, typer.Option("--time", "-t", help="Time filter: 'day', 'week', 'month', 'year', 'all'.")] = "week"
):
    """
    Scrapes posts and their comments from a specific subreddit.
    """
    try:
        client = RedditClient()
        client.scrape_subreddit(subreddit_name=subreddit, limit=limit, time_filter=time_filter)
        print(f"[bold green]Scraping task for r/{subreddit} completed.[/bold green]")
    except Exception as e:
        print(f"[bold red]An error occurred during scraping setup: {e}[/bold red]")
