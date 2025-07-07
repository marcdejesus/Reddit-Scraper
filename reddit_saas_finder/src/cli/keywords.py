
import typer
from rich.console import Console
from utils.keywords import KeywordManager

app = typer.Typer(help="Manage custom keywords for NLP processing.")
console = Console()
keyword_manager = KeywordManager()

@app.command("add")
def add_keyword(
    keyword: str = typer.Argument(..., help="The keyword to add."),
    category: str = typer.Option(None, "--category", "-c", help="The category to associate with the keyword.")
):
    """
    Adds a new pain point keyword.
    """
    keyword_manager.add_pain_point_keyword(keyword, category)

@app.command("remove")
def remove_keyword(
    keyword: str = typer.Argument(..., help="The keyword to remove.")
):
    """
    Removes a pain point keyword.
    """
    keyword_manager.remove_keyword(keyword)

@app.command("export")
def export_keywords(
    output_file: str = typer.Option("keywords.yaml", "--output", "-o", help="The file to export keywords to."),
    format: str = typer.Option("yaml", "--format", "-f", help="The format to export in (currently only yaml is supported).")
):
    """
    Exports the current keywords to a file.
    """
    keyword_manager.export_keywords(output_file, format)

@app.command("list")
def list_keywords():
    """
    Lists all configured pain point keywords.
    """
    keywords = keyword_manager.get_pain_point_keywords()
    if not keywords:
        console.print("[yellow]No pain point keywords configured.[/yellow]")
        return
    
    console.print("[bold green]Configured Pain Point Keywords:[/bold green]")
    for keyword in keywords:
        console.print(f"- {keyword}")

if __name__ == "__main__":
    app() 