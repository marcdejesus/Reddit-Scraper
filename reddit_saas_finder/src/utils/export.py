"""Handles exporting data to various formats and generating reports."""
import csv
import json
import yaml
import os
from datetime import datetime
from rich.console import Console
from typing import List, Dict, Any

from data.database import (
    get_opportunities, 
    get_pain_points, 
    get_category_distribution,
    Opportunity,
    PainPoint
)

console = Console()

# This is a placeholder until trend analysis is implemented
def analyze_trends() -> Dict[str, Any]:
    """Mock function for trend analysis."""
    return {"trending_topic": "AI in copywriting", "growth": "25%"}


class DataExporter:
    """
    Manages exporting data to various formats and generating summary reports.
    """
    def __init__(self, export_dir: str = "reddit_saas_finder/exports"):
        """
        Initializes the DataExporter.

        Args:
            export_dir (str, optional): The directory where exported files
                will be saved. Defaults to "reddit_saas_finder/exports".
        """
        self.export_dir = export_dir
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    def _get_filename(self, name: str, format: str) -> str:
        """
        Generates a timestamped filename if one is not provided.

        Args:
            name (str): The base name for the file (e.g., 'opportunities').
            format (str): The file extension (e.g., 'csv').

        Returns:
            str: The full path for the new file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.export_dir, f"{name}_{timestamp}.{format}")

    def export_data(self, data: List[Any], data_type: str, format: str, filename: str = None):
        """
        Exports a list of data objects to the specified format (CSV, JSON, or YAML).

        Args:
            data (List[Any]): A list of data objects (e.g., Opportunity or PainPoint).
            data_type (str): A string representing the type of data (e.g., 'opportunities').
            format (str): The target format ('csv', 'json', 'yaml').
            filename (str, optional): The name of the output file. If not provided,
                a timestamped name is generated. Defaults to None.
        """
        if not filename:
            filename = self._get_filename(data_type, format)

        if not data:
            console.print(f"[bold yellow]No {data_type} data to export.[/bold yellow]")
            return

        try:
            # Convert data objects to dictionaries for export
            data_dicts = [item.__dict__ for item in data] if hasattr(data[0], '__dict__') else data

            if format == 'csv':
                self._export_to_csv(data_dicts, filename)
            elif format == 'json':
                self._export_to_json(data_dicts, filename)
            elif format == 'yaml':
                self._export_to_yaml(data_dicts, filename)
            else:
                console.print(f"[bold red]Unsupported format: {format}[/bold red]")
                return
            
            console.print(f"[bold green]Successfully exported {data_type} to {filename}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]An error occurred during export: {e}[/bold red]")

    def _export_to_csv(self, data: List[Dict[str, Any]], filename: str):
        """Helper to export data to a CSV file."""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    def _export_to_json(self, data: List[Dict[str, Any]], filename: str):
        """Helper to export data to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def _export_to_yaml(self, data: List[Dict[str, Any]], filename: str):
        """Helper to export data to a YAML file."""
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False)

    def generate_report(self, format: str = 'txt', filename: str = None):
        """
        Generates a summary report in the specified format (TXT or JSON).

        Args:
            format (str, optional): The format for the report. Defaults to 'txt'.
            filename (str, optional): The name of the output file. If not provided,
                a timestamped name is generated. Defaults to None.
        """
        if not filename:
            filename = self._get_filename("report", format)
            
        summary_data = self._generate_summary_data()
        
        try:
            if format == 'txt':
                report_content = self._format_text_report(summary_data)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report_content)
            elif format == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(summary_data, f, indent=4)
            else:
                console.print(f"[bold red]Unsupported report format: {format}[/bold red]")
                return

            console.print(f"[bold green]Successfully generated report to {filename}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]An error occurred generating report: {e}[/bold red]")
        
    def _generate_summary_data(self) -> Dict[str, Any]:
        """
        Gathers and compiles data needed for the summary report.

        Returns:
            Dict[str, Any]: A dictionary containing summary statistics, top opportunities,
                            category distributions, and trend analysis.
        """
        top_opportunities = get_opportunities(limit=5)
        category_dist = get_category_distribution()
        trends = analyze_trends()
        
        return {
            "report_generated_at": datetime.now().isoformat(),
            "summary_stats": {
                "total_opportunities": len(get_opportunities(limit=1000)),
                "total_pain_points": len(get_pain_points()),
                "top_category": category_dist[0][0] if category_dist else "N/A"
            },
            "top_opportunities": [opp.__dict__ for opp in top_opportunities],
            "category_distribution": dict(category_dist),
            "trend_analysis": trends
        }
        
    def _format_text_report(self, summary: Dict[str, Any]) -> str:
        """
        Formats the summary data into a human-readable text report.

        Args:
            summary (Dict[str, Any]): The dictionary of summary data.

        Returns:
            str: A formatted string containing the full report.
        """
        report_lines = [
            "="*50,
            " Reddit SaaS Opportunity Finder - Summary Report",
            "="*50,
            f"Report Generated: {summary['report_generated_at']}\n",
            "[Summary Statistics]",
            f"  - Total Opportunities Found: {summary['summary_stats']['total_opportunities']}",
            f"  - Total Pain Points Detected: {summary['summary_stats']['total_pain_points']}",
            f"  - Top Category: {summary['summary_stats']['top_category']}\n",
            "[Top 5 Opportunities]"
        ]
        
        for opp in summary['top_opportunities']:
            report_lines.append(f"  - ID: {opp['id']}, Title: {opp['title']}, Score: {opp['total_score']:.3f}")
        report_lines.append("\n")
        
        report_lines.append("[Category Distribution]")
        for category, count in summary['category_distribution'].items():
            report_lines.append(f"  - {category}: {count}")
        report_lines.append("\n")

        report_lines.append("[Trend Analysis]")
        for key, value in summary['trend_analysis'].items():
            report_lines.append(f"  - {key.replace('_', ' ').title()}: {value}")
        report_lines.append("\n" + "="*50)
        
        return "\n".join(report_lines) 