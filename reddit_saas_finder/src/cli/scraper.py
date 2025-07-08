"""Handles all Reddit data collection."""
import typer
import yaml
from rich import print
from data.reddit_client import RedditClient
from typing_extensions import Annotated
from utils.config import ConfigManager


app = typer.Typer()

@app.command()
def single(
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

@app.command()
def batch(
    config_file: Annotated[str, typer.Option("--config", "-c", help="Path to the subreddits YAML config file.")] = "src/config/subreddits.yaml",
    limit: Annotated[int, typer.Option("--limit", "-l", help="The maximum number of posts to scrape per subreddit.")] = 100,
    time_filter: Annotated[str, typer.Option("--time", "-t", help="Time filter: 'day', 'week', 'month', 'year', 'all'.")] = "week"
):
    """
    Scrapes posts and comments from a batch of subreddits defined in a YAML file.
    """
    try:
        config_manager = ConfigManager()
        primary, secondary = config_manager.load_subreddits()
        all_subreddits = primary + secondary

        if not all_subreddits:
            print("[bold red]No subreddits found in the config file.[/bold red]")
            return

        client = RedditClient()
        print(f"Starting batch scrape for {len(all_subreddits)} subreddits...")
        for subreddit_name in all_subreddits:
            print(f"Scraping r/{subreddit_name}...")
            client.scrape_subreddit(subreddit_name=subreddit_name, limit=limit, time_filter=time_filter)
        print("[bold green]Batch scraping completed.[/bold green]")

    except FileNotFoundError:
        print(f"[bold red]Error: Config file not found at {config_file}[/bold red]")
    except Exception as e:
        print(f"[bold red]An error occurred during batch scraping: {e}[/bold red]")

if __name__ == "__main__":
    app()
