"""Contains data validation functions."""

import sqlite3
import pandas as pd
from rich.console import Console

console = Console()

class DataValidator:
    """
    Performs data quality checks on scraped Reddit data.
    """
    def __init__(self, db_connection):
        self.conn = db_connection
        self.report = {}

    def validate_data(self, spam_threshold: float = 0.5, min_post_length: int = 20, min_comment_length: int = 10, duplication_threshold: float = 0.9):
        """
        Runs all data validation checks.
        """
        console.print("[bold cyan]Starting data validation...[/bold cyan]")
        posts_df = pd.read_sql_query("SELECT * FROM posts", self.conn)
        comments_df = pd.read_sql_query("SELECT * FROM comments", self.conn)

        total_posts = len(posts_df)
        total_comments = len(comments_df)

        # Completeness check
        critical_post_fields = ['id', 'title', 'subreddit', 'created_utc', 'author']
        missing_posts = posts_df[critical_post_fields].isnull().any(axis=1).sum()

        critical_comment_fields = ['id', 'post_id', 'content', 'created_utc', 'author']
        missing_comments = comments_df[critical_comment_fields].isnull().any(axis=1).sum()

        # Duplication check (simple check on content)
        duplicate_posts = posts_df.duplicated(subset=['title', 'content'], keep='first').sum()
        duplicate_comments = comments_df.duplicated(subset=['content'], keep='first').sum()

        # Spam/Low-quality check (example: very short content or low score)
        # This can be made more sophisticated.
        spam_posts = posts_df[(posts_df['content'].str.len() < min_post_length) | (posts_df['score'] < 1)].shape[0]
        spam_comments = comments_df[(comments_df['content'].str.len() < min_comment_length) | (comments_df['score'] < 1)].shape[0]


        self.report = {
            "posts": {
                "total": total_posts,
                "missing_critical_fields": missing_posts,
                "duplicates": duplicate_posts,
                "spam_or_low_quality": spam_posts,
                "valid": total_posts - missing_posts - duplicate_posts - spam_posts
            },
            "comments": {
                "total": total_comments,
                "missing_critical_fields": missing_comments,
                "duplicates": duplicate_comments,
                "spam_or_low_quality": spam_comments,
                "valid": total_comments - missing_comments - duplicate_comments - spam_comments
            }
        }
        console.print("[bold green]Data validation complete.[/bold green]")


    def generate_quality_report(self):
        """
        Generates and displays a quality report.
        """
        if not self.report:
            console.print("[yellow]No report generated. Run validation first.[/yellow]")
            return
        
        from rich.table import Table
        from rich.panel import Panel

        # Post statistics
        post_stats = self.report['posts']
        post_table = Table(title="Post Data Quality Report")
        post_table.add_column("Metric", style="cyan")
        post_table.add_column("Count", style="magenta")
        post_table.add_column("% of Total", style="green")

        post_table.add_row("Total Posts", str(post_stats['total']), "100%")
        post_table.add_row("Valid Posts", str(post_stats['valid']), f"{(post_stats['valid'] / post_stats['total'] * 100):.2f}%" if post_stats['total'] > 0 else "0.00%")
        post_table.add_row("Missing Critical Fields", str(post_stats['missing_critical_fields']), f"{(post_stats['missing_critical_fields'] / post_stats['total'] * 100):.2f}%" if post_stats['total'] > 0 else "0.00%")
        post_table.add_row("Duplicate Posts", str(post_stats['duplicates']), f"{(post_stats['duplicates'] / post_stats['total'] * 100):.2f}%" if post_stats['total'] > 0 else "0.00%")
        post_table.add_row("Spam/Low-Quality", str(post_stats['spam_or_low_quality']), f"{(post_stats['spam_or_low_quality'] / post_stats['total'] * 100):.2f}%" if post_stats['total'] > 0 else "0.00%")

        # Comment statistics
        comment_stats = self.report['comments']
        comment_table = Table(title="Comment Data Quality Report")
        comment_table.add_column("Metric", style="cyan")
        comment_table.add_column("Count", style="magenta")
        comment_table.add_column("% of Total", style="green")

        comment_table.add_row("Total Comments", str(comment_stats['total']), "100%")
        comment_table.add_row("Valid Comments", str(comment_stats['valid']), f"{(comment_stats['valid'] / comment_stats['total'] * 100):.2f}%" if comment_stats['total'] > 0 else "0.00%")
        comment_table.add_row("Missing Critical Fields", str(comment_stats['missing_critical_fields']), f"{(comment_stats['missing_critical_fields'] / comment_stats['total'] * 100):.2f}%" if comment_stats['total'] > 0 else "0.00%")
        comment_table.add_row("Duplicate Comments", str(comment_stats['duplicates']), f"{(comment_stats['duplicates'] / comment_stats['total'] * 100):.2f}%" if comment_stats['total'] > 0 else "0.00%")
        comment_table.add_row("Spam/Low-Quality", str(comment_stats['spam_or_low_quality']), f"{(comment_stats['spam_or_low_quality'] / comment_stats['total'] * 100):.2f}%" if comment_stats['total'] > 0 else "0.00%")


        console.print(Panel(post_table, expand=False))
        console.print(Panel(comment_table, expand=False)) 