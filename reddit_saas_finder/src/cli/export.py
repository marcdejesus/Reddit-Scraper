"""Handles the CLI commands for exporting data and generating reports."""
import typer
from rich import print
from reddit_saas_finder.src.utils.export import DataExporter
from reddit_saas_finder.src.data.database import get_opportunities, get_pain_points

app = typer.Typer(help="Export data and generate reports.")
exporter = DataExporter(export_dir="reddit_saas_finder/exports")

@app.command()
def export(
    opportunities: bool = typer.Option(False, "--opportunities", help="Export opportunities data."),
    pain_points: bool = typer.Option(False, "--pain-points", help="Export pain points data."),
    format: str = typer.Option("csv", "--format", "-f", help="Export format (csv, json, yaml)."),
    output: str = typer.Option(None, "--output", "-o", help="The name of the output file."),
):
    """
    Export opportunities or pain points to a file.
    """
    if not opportunities and not pain_points:
        print("[bold red]Error: Please specify what to export, e.g., --opportunities or --pain-points[/bold red]")
        raise typer.Exit(code=1)

    if opportunities:
        data_to_export = get_opportunities(limit=1000)
        exporter.export_data(data_to_export, 'opportunities', format, output)

    if pain_points:
        data_to_export = get_pain_points()
        # Since get_pain_points returns mock data that isn't a list of objects, we handle it directly
        exporter.export_data(data_to_export, 'pain_points', format, output)

@app.command()
def report(
    summary: bool = typer.Option(True, "--summary", help="Generate a summary report (default)."),
    comprehensive: bool = typer.Option(False, "--comprehensive", help="Generate a comprehensive report (not yet implemented)."),
    format: str = typer.Option("txt", "--format", "-f", help="Report format (txt, json)."),
    output: str = typer.Option(None, "--output", "-o", help="The name of the output file."),
):
    """
    Generate a summary report of the findings.
    """
    if comprehensive:
        print("[bold yellow]Warning: Comprehensive report is not yet implemented. Generating a summary report instead.[/bold yellow]")
    
    exporter.generate_report(format, output) 