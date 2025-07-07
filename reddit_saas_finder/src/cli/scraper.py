"""Handles all Reddit data collection."""
import typer
from rich import print
from data.reddit_client import RedditClient

app = typer.Typer()

@app.command()
def subreddit(
    subreddit: str = typer.Option("entrepreneur", "--name", "-n", help="The subreddit to scrape."),
    limit: int = typer.Option(100, "--limit", "-l", help="The maximum number of posts to scrape."),
    time_filter: str = typer.Option("week", "--time", "-t", help="The time filter for scraping (e.g., 'day', 'week', 'month', 'year', 'all').")
):
    """
    Scrapes posts and their comments from a specific subreddit.

    This command connects to the Reddit API, fetches the top posts from the
    specified subreddit based on the time filter, and saves them along with
    their comments into the database for later processing.

    Args:
        subreddit (str): The name of the subreddit to scrape.
        limit (int): The maximum number of posts to fetch.
        time_filter (str): The time window to filter posts by (e.g., 'day', 'week').
    """
    try:
        client = RedditClient()
        client.scrape_subreddit(subreddit_name=subreddit, limit=limit, time_filter=time_filter)
        print(f"[bold green]Scraping task for r/{subreddit} completed.[/bold green]")
    except Exception as e:
        print(f"[bold red]An error occurred during scraping setup: {e}[/bold red]")
