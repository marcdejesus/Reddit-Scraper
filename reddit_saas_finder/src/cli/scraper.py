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
    Scrapes a specific subreddit for posts and comments.
    """
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
