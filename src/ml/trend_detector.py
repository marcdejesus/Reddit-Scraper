"""Detects trends in opportunities and pain points over time."""
import json
import pandas as pd
from collections import Counter
from rich.console import Console

from reddit_saas_finder.src.data.database import get_pain_points, get_opportunities

console = Console()

class TrendAnalyzer:
    """
    Analyzes trends in pain points and opportunities over time.
    """

    def analyze_opportunity_trends(self, days=30):
        """
        Analyzes the frequency of pain points over a given number of days to spot trends.
        This is a simplified implementation focusing on overall pain point velocity.
        """
        console.print(f"Analyzing pain point trends over the last {days} days...", style="bold blue")
        pain_points = get_pain_points()
        if not pain_points:
            return {"error": "No pain points found to analyze."}

        df = pd.DataFrame(pain_points)
        df['processed_at'] = pd.to_datetime(df['processed_at'])
        
        # Filter by date range
        recent_df = df[df['processed_at'] >= (pd.Timestamp.now() - pd.Timedelta(days=days))]
        if recent_df.empty:
            return {"summary": "No pain points found in the specified date range.", "trends": []}

        # Group by day and count
        daily_counts = recent_df.set_index('processed_at').resample('D').size()
        
        # Simple trend detection
        if len(daily_counts) < 2:
            trend = "stable"
        else:
            first_half_avg = daily_counts.iloc[:len(daily_counts)//2].mean()
            second_half_avg = daily_counts.iloc[len(daily_counts)//2:].mean()
            if second_half_avg > first_half_avg * 1.2:
                trend = "increasing"
            elif second_half_avg < first_half_avg * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"
        
        return {
            "summary": f"Overall trend is {trend}.",
            "daily_counts": daily_counts.to_dict()
        }

    def detect_seasonal_patterns(self):
        """
        Identifies seasonal patterns by analyzing pain point frequency by month.
        """
        console.print("Detecting seasonal patterns...", style="bold blue")
        pain_points = get_pain_points()
        if not pain_points:
            return {"error": "No pain points found to analyze."}

        df = pd.DataFrame(pain_points)
        df['month'] = pd.to_datetime(df['processed_at']).dt.strftime('%B')
        monthly_counts = Counter(df['month'])
        
        return {
            "summary": "Pain point mentions per month.",
            "monthly_counts": dict(monthly_counts)
        }

    def predict_opportunity_growth(self, opportunity_id: int):
        """
        Predicts the growth of a single opportunity based on the trend of its associated pain points.
        Note: This is a mock implementation. A real version would need more sophisticated modeling.
        """
        console.print(f"Predicting growth for opportunity ID {opportunity_id}...", style="bold blue")
        # This is a placeholder for a real implementation.
        # A real implementation would fetch the opportunity, get its pain point IDs,
        # fetch those pain points, and then perform time-series analysis on their creation dates.
        # For now, we'll return a dummy value.
        
        # In a real scenario, you'd perform linear regression or a similar analysis
        # on the timestamps of the associated pain points.
        
        # Returning a mock probability
        return {"opportunity_id": opportunity_id, "growth_prediction": 0.65, "status": "Mock data"} 