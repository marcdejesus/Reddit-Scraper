import typer
from reddit_saas_finder.src.data.database import initialize_database
from reddit_saas_finder.src.data.reddit_client import RedditClient
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
def process():
    """Processes the NLP pipeline."""
    print("Processing NLP pipeline...")

@app.command()
def opportunities():
    """Scores opportunities."""
    print("Scoring opportunities...")

@app.command()
def init_db():
    """Initializes the database."""
    initialize_database()

if __name__ == "__main__":
    app() 