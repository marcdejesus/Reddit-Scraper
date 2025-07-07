"""Detects trends using machine learning.""" 

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import numpy as np

from data.database import get_db_connection

class TrendDetector:
    """
    Analyzes time-series data to detect trends, seasonality, and predict growth.

    This class queries the database for opportunity and pain point data, then
    applies statistical methods and simple models to uncover temporal patterns.
    """
    def __init__(self, db_connection):
        """
        Initializes the TrendDetector.

        Args:
            db_connection: An active SQLite database connection.
        """
        self.conn = db_connection

    def analyze_opportunity_trends(self, days: int = 30) -> list:
        """
        Analyzes the trend of pain point mentions for opportunities over a period.

        It compares the number of mentions in the first half of the period to
        the second half to determine if the trend is increasing, decreasing, or stable.

        Args:
            days (int): The number of days to look back for trend analysis.

        Returns:
            list: A list of dictionaries, each containing opportunity details
                  and its calculated trend ('increasing', 'decreasing', 'stable').
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = """
        SELECT
            o.id,
            o.title,
            o.total_score,
            p.created_utc
        FROM opportunities o
        JOIN json_each(o.pain_point_ids) j ON 1
        JOIN pain_points pp ON pp.id = j.value
        -- Joining with both posts and comments to get creation time
        LEFT JOIN posts p ON pp.source_type = 'post' AND pp.source_id = p.id
        LEFT JOIN comments c ON pp.source_type = 'comment' AND pp.source_id = c.id
        WHERE COALESCE(p.created_utc, c.created_utc) >= ?
        """
        
        # The above query is not quite right because pain_points doesn't have created_utc
        # and joining posts and comments and using COALESCE is tricky.
        # Let's get pain points with their creation dates first.

        pain_points_query = """
        SELECT
            pp.id,
            COALESCE(p.created_utc, c.created_utc) as created_utc
        FROM pain_points pp
        LEFT JOIN posts p ON pp.source_type = 'post' AND pp.source_id = p.id
        LEFT JOIN comments c ON pp.source_type = 'comment' AND pp.source_id = c.id
        WHERE COALESCE(p.created_utc, c.created_utc) IS NOT NULL
          AND DATETIME(COALESCE(p.created_utc, c.created_utc)) >= DATETIME(?)
        """

        df_pain_points = pd.read_sql_query(pain_points_query, self.conn, params=(start_date,))
        df_pain_points['created_utc'] = pd.to_datetime(df_pain_points['created_utc'])

        opportunities_query = "SELECT id, title, total_score, pain_point_ids FROM opportunities"
        df_opportunities = pd.read_sql_query(opportunities_query, self.conn)
        
        results = []

        for _, opp in df_opportunities.iterrows():
            pain_point_ids = pd.read_json(opp['pain_point_ids'])
            if not len(pain_point_ids):
                continue
            
            opp_pain_points_df = df_pain_points[df_pain_points['id'].isin(pain_point_ids[0])]
            
            if len(opp_pain_points_df) < 2:
                trend = "stable"
            else:
                # Simple trend calculation: compare first half vs second half
                mid_point_date = start_date + timedelta(days=days/2)
                first_half_count = opp_pain_points_df[opp_pain_points_df['created_utc'] < mid_point_date].shape[0]
                second_half_count = opp_pain_points_df[opp_pain_points_df['created_utc'] >= mid_point_date].shape[0]

                if second_half_count > first_half_count * 1.2: # 20% increase
                    trend = "increasing"
                elif first_half_count > second_half_count * 1.2: # 20% decrease
                    trend = "decreasing"
                else:
                    trend = "stable"

            results.append({
                "id": opp["id"],
                "title": opp["title"],
                "total_score": opp["total_score"],
                "trend": trend,
            })
            
        return results

    def detect_seasonal_patterns(self) -> dict:
        """
        Identifies seasonal patterns in pain point frequency by month.

        This can help identify if certain problems are more common during
        specific times of the year.

        Returns:
            dict: A dictionary with month names as keys and pain point counts as values.
        """
        query = """
        SELECT
            STRFTIME('%m', COALESCE(p.created_utc, c.created_utc)) as month,
            COUNT(pp.id) as count
        FROM pain_points pp
        LEFT JOIN posts p ON pp.source_type = 'post' AND pp.source_id = p.id
        LEFT JOIN comments c ON pp.source_type = 'comment' AND pp.source_id = c.id
        WHERE month IS NOT NULL
        GROUP BY month
        ORDER BY month
        """
        df = pd.read_sql_query(query, self.conn)
        
        month_map = {
            "01": "January", "02": "February", "03": "March", "04": "April",
            "05": "May", "06": "June", "07": "July", "08": "August",
            "09": "September", "10": "October", "11": "November", "12": "December"
        }
        
        return {month_map[row['month']]: row['count'] for _, row in df.iterrows()}

    def predict_opportunity_growth(self, opportunity_id: int) -> float:
        """
        Predicts the growth of an opportunity using linear regression on daily mentions.

        It calculates the slope of the trend line for pain point mentions related
        to an opportunity and converts it into a growth probability score.

        Args:
            opportunity_id (int): The ID of the opportunity to predict.

        Returns:
            float: A float between 0 and 1 representing the probability of growth.
                   Returns 0.0 if the opportunity is not found or has no data.
                   Returns 0.5 if there is insufficient data for a prediction.
        """
        
        query = """
        SELECT
            pp.id,
            COALESCE(p.created_utc, c.created_utc) as created_utc
        FROM pain_points pp
        JOIN opportunities o ON json_extract(o.pain_point_ids, '$[0]') = pp.id AND o.id = ?
        LEFT JOIN posts p ON pp.source_type = 'post' AND pp.source_id = p.id
        LEFT JOIN comments c ON pp.source_type = 'comment' AND pp.source_id = c.id
        WHERE created_utc IS NOT NULL
        """
        # This query is also wrong. I need to get all pain points for an opportunity.
        opp_query = "SELECT pain_point_ids FROM opportunities WHERE id = ?"
        cursor = self.conn.cursor()
        cursor.execute(opp_query, (opportunity_id,))
        row = cursor.fetchone()
        if not row:
            return 0.0

        pain_point_ids = tuple(pd.read_json(row[0])[0].tolist())

        if not pain_point_ids:
            return 0.0

        placeholders = ', '.join('?' for _ in pain_point_ids)
        pain_points_query = f"""
        SELECT
            COALESCE(p.created_utc, c.created_utc) as created_utc
        FROM pain_points pp
        LEFT JOIN posts p ON pp.source_type = 'post' AND pp.source_id = p.id
        LEFT JOIN comments c ON pp.source_type = 'comment' AND pp.source_id = c.id
        WHERE pp.id IN ({placeholders})
        """

        df = pd.read_sql_query(pain_points_query, self.conn, params=pain_point_ids)
        df['created_utc'] = pd.to_datetime(df['created_utc'])
        df = df.set_index('created_utc').resample('D').size().reset_index(name='count')

        if len(df) < 5:
            return 0.5 # Not enough data, neutral prediction

        df['time'] = (df['created_utc'] - df['created_utc'].min()).dt.days
        
        X = df[['time']]
        y = df['count']
        
        model = LinearRegression()
        model.fit(X, y)
        
        # The slope of the regression line indicates the trend
        slope = model.coef_[0]
        
        # Normalize slope to a 0-1 probability-like score
        # This is a simple heuristic. A positive slope means growth.
        # We can use sigmoid to squash the slope to a 0-1 range.
        # A larger positive slope means higher probability of growth.
        probability = 1 / (1 + np.exp(-slope))
        
        return probability 