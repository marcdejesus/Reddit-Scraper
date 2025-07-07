import typer
from reddit_saas_finder.src.data.database import initialize_database

app = typer.Typer()

@app.command()
def init():
    """Initializes the Reddit SaaS Finder."""
    print("Initializing Reddit SaaS Finder...")

@app.command()
def scrape():
    """Scrapes Reddit data."""
    print("Scraping Reddit data...")

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