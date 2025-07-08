"""Handles the CLI commands for exporting data and generating reports."""
import typer
from rich import print
from utils.export import DataExporter
from data.database import get_opportunities, get_pain_points
from typing_extensions import Annotated

exporter = DataExporter(export_dir="reddit_saas_finder/exports")

def export(
    opportunities: Annotated[bool, typer.Option("--opportunities", help="Export opportunities data.")] = False,
    pain_points: Annotated[bool, typer.Option("--pain-points", help="Export pain points data.")] = False,
    format: Annotated[str, typer.Option("--format", "-f", help="Export format (csv, json, yaml).")] = "csv",
    output: Annotated[str, typer.Option("--output", "-o", help="The name of the output file.")] = None,
):
    """
    Exports generated data to various file formats.
    """
    if not opportunities and not pain_points:
        print("[bold red]Error: Please specify what to export, e.g., --opportunities or --pain-points[/bold red]")
        raise typer.Exit(code=1)

    if opportunities:
        data_to_export = get_opportunities(limit=1000)
        exporter.export_data(data_to_export, 'opportunities', format, output)

    if pain_points:
        data_to_export = get_pain_points()
        exporter.export_data(data_to_export, 'pain_points', format, output)

def report(
    summary: Annotated[bool, typer.Option("--summary", help="Generate a summary report (default).")] = True,
    comprehensive: Annotated[bool, typer.Option("--comprehensive", help="Generate a comprehensive report.")] = False,
    format: Annotated[str, typer.Option("--format", "-f", help="Report format (txt, json).")] = "txt",
    output: Annotated[str, typer.Option("--output", "-o", help="The name of the output file.")] = None,
):
    """
    Generates a summary report of the analysis findings.
    """
    if comprehensive:
        print("[bold yellow]Warning: Comprehensive report is not yet implemented. Generating a summary report instead.[/bold yellow]")
    
    exporter.generate_report(format, output) 