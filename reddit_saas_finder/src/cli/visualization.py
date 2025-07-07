"""Handles terminal-based data visualization."""
import typer
from rich import print
from rich.console import Console
from rich.table import Table

from data.database import get_opportunities, get_category_distribution

app = typer.Typer()
console = Console()

class TerminalVisualizer:
    """
    Handles displaying data in formatted terminal tables and charts.
    """
    def display_opportunities_table(self, limit: int = 20):
        """Displays top opportunities in a formatted table."""
        opportunities = get_opportunities(limit)
        if not opportunities:
            console.print("[bold yellow]No opportunities found to display.[/bold yellow]")
            return

        table = Table(title=f"Top {limit} SaaS Opportunities", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=6)
        table.add_column("Title", style="bold", min_width=40)
        table.add_column("Category", style="cyan", width=20)
        table.add_column("Score", style="green", justify="right")
        table.add_column("Pain Points", style="yellow", justify="right")
        
        for opp in opportunities:
            table.add_row(
                str(opp.id),
                opp.title,
                opp.category,
                f"{opp.total_score:.3f}",
                str(opp.pain_point_count)
            )
        
        console.print(table)

    def display_category_distribution(self):
        """Displays the distribution of opportunities across categories."""
        distribution = get_category_distribution()
        if not distribution:
            console.print("[bold yellow]No category data to display.[/bold yellow]")
            return

        console.print("\n[bold]Opportunity Distribution by Category:[/bold]")
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Category", style="cyan")
        table.add_column("Count", style="green", justify="right")

        for category, count in distribution:
            table.add_row(category, str(count))
            
        console.print(table)

@app.command("table")
def show_table(
    limit: int = typer.Option(20, "--limit", "-l", help="Limit the number of opportunities to display.")
):
    """Display opportunities in a table."""
    visualizer = TerminalVisualizer()
    visualizer.display_opportunities_table(limit)

@app.command("categories")
def show_categories():
    """Display category distribution chart."""
    visualizer = TerminalVisualizer()
    visualizer.display_category_distribution()

if __name__ == "__main__":
    app()