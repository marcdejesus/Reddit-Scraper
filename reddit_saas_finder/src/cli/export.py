"""Handles the CLI commands for exporting data and generating reports."""
import typer
from rich import print
from utils.export import DataExporter
from data.database import get_opportunities, get_pain_points

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
    Exports generated data to various file formats.

    This command allows you to export either the generated opportunities or the
    detected pain points into formats like CSV, JSON, or YAML.

    Args:
        opportunities (bool): Flag to export opportunities.
        pain_points (bool): Flag to export pain points.
        format (str): The desired output format.
        output (str): Optional name for the output file.
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
    Generates a summary report of the analysis findings.

    This command creates a text or JSON report summarizing the key insights,
    such as top opportunities and common pain points.

    Args:
        summary (bool): Flag to generate a summary report.
        comprehensive (bool): Flag for a more detailed report (not implemented).
        format (str): The desired report format.
        output (str): Optional name for the output file.
    """
    if comprehensive:
        print("[bold yellow]Warning: Comprehensive report is not yet implemented. Generating a summary report instead.[/bold yellow]")
    
    exporter.generate_report(format, output) 