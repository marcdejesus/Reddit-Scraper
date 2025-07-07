"""Handles the visualization of data in the terminal."""
import sqlite3
from rich.console import Console
from rich.table import Table
from collections import Counter

from reddit_saas_finder.src.data.database import DB_PATH

class TerminalVisualizer:
    """
    Handles the visualization of data in the terminal using the Rich library.
    """
    def __init__(self):
        self.console = Console()
        self.db_path = DB_PATH

    def display_opportunities_table(self, limit: int = 20):
        """
        Fetches opportunities from the database and displays them in a formatted table.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM opportunities ORDER BY total_score DESC LIMIT ?", (limit,))
                opportunities = [dict(row) for row in cursor.fetchall()]

                if not opportunities:
                    self.console.print("[bold yellow]No opportunities found in the database.[/bold yellow]")
                    return

                table = Table(title=f"Top {limit} SaaS Opportunities", show_header=True, header_style="bold magenta")
                table.add_column("ID", style="dim", width=6)
                table.add_column("Title", style="bold", min_width=40)
                table.add_column("Category", style="cyan", width=15)
                table.add_column("Market Score", style="green", justify="right")
                table.add_column("WTP Score", style="green", justify="right")
                table.add_column("Total Score", style="bold green", justify="right")

                for opp in opportunities:
                    table.add_row(
                        str(opp['id']),
                        opp['title'][:80] + "..." if len(opp['title']) > 80 else opp['title'],
                        opp['category'],
                        f"{opp['market_score']:.2f}",
                        f"{opp['willingness_to_pay_score']:.2f}",
                        f"{opp['total_score']:.2f}",
                    )
                
                self.console.print(table)

        except sqlite3.Error as e:
            self.console.print(f"[bold red]Database error: {e}[/bold red]")

    def display_category_distribution(self):
        """
        Fetches opportunities and displays the distribution of categories as a bar chart.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT category FROM opportunities")
                categories = [row[0] for row in cursor.fetchall()]

                if not categories:
                    self.console.print("[bold yellow]No opportunities found to generate category distribution.[/bold yellow]")
                    return

                category_counts = Counter(categories)
                
                self.console.print("\n[bold]Category Distribution:[/bold]")
                table = Table(show_header=False, show_edge=False, box=None)
                table.add_column("Category", style="cyan")
                table.add_column("Count", style="green", justify="right")
                table.add_column("Chart")

                max_count = max(category_counts.values()) if category_counts else 0
                
                for category, count in category_counts.most_common():
                    bar_length = int((count / max_count) * 30) if max_count > 0 else 0
                    bar = "█" * bar_length
                    table.add_row(category, str(count), bar)

                self.console.print(table)

        except sqlite3.Error as e:
            self.console.print(f"[bold red]Database error: {e}[/bold red]") 