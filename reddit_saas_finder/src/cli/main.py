import typer

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

if __name__ == "__main__":
    app() 