"""Scores opportunities using machine learning models."""
import sqlite3
import logging
import re
from datetime import datetime
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rich.progress import track
import json

from src.data.database import get_pain_points, save_opportunities

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OpportunityScorer:
    """
    Analyzes and scores potential SaaS opportunities based on pain points.

    This class groups similar pain points, calculates various scores
    (market, frequency, willingness to pay), and generates a final
    opportunity score.
    """
    def __init__(self, pain_points, min_pain_points=5, min_score=0.5):
        """Initializes the OpportunityScorer."""
        self.pain_points = pain_points
        self.min_pain_points = min_pain_points
        self.min_score = min_score

    def _group_similar_pain_points(self, similarity_threshold=0.7):
        """
        Groups similar pain points using TF-IDF and cosine similarity.

        This helps to identify underlying themes and aggregate related user problems.

        Args:
            pain_points (list): A list of pain point dictionaries.
            similarity_threshold (float, optional): The threshold for grouping.
                Defaults to 0.7.

        Returns:
            list: A list of groups, where each group is a list of pain points.
        """
        if not self.pain_points:
            return []

        # Extract content for vectorization
        contents = [pp['content'] for pp in self.pain_points]
        
        # Vectorize the text using TF-IDF
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(contents)
        
        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        groups = []
        visited = [False] * len(self.pain_points)
        
        for i in range(len(self.pain_points)):
            if visited[i]:
                continue
            
            # Start a new group with the current pain point
            current_group = [self.pain_points[i]]
            visited[i] = True
            
            # Find similar pain points
            for j in range(i + 1, len(self.pain_points)):
                if not visited[j] and similarity_matrix[i, j] >= similarity_threshold:
                    current_group.append(self.pain_points[j])
                    visited[j] = True
            
            groups.append(current_group)
            
        return groups

    def _calculate_market_score(self, pain_point_group):
        """
        Calculates a market score for a group of pain points.

        The score is based on frequency, reach (unique users), and the
        diversity of subreddits where the pain points appear.

        Args:
            pain_point_group (list): A list of pain points in a group.

        Returns:
            float: The calculated market score (0.0 to 1.0).
        """
        frequency = len(pain_point_group)
        # Placeholder for unique_users and subreddit_diversity, needs more data
        unique_users = len(set(pp['source_id'] for pp in pain_point_group))
        subreddit_diversity = len(set(p['subreddit'] for p in pain_point_group if p['subreddit']))

        market_score = (frequency * 0.4 + unique_users * 0.4 + subreddit_diversity * 0.2) / 100
        return min(1.0, market_score)

    def _detect_willingness_to_pay(self, text):
        """
        Detects keywords indicating a willingness to pay in a given text.

        Args:
            text (str): The text to analyze.

        Returns:
            float: A score indicating the strength of willingness to pay.
        """
        pay_indicators = [
            r'\$\d+', r'budget', r'pay for', r'worth paying', r'subscription',
            r'premium', r'paid (tool|service|app)', r'enterprise'
        ]
        score = sum(0.2 for indicator in pay_indicators if re.search(indicator, text, re.IGNORECASE))
        return min(1.0, score)

    def generate_opportunities(self):
        """
        The main function to generate, score, and save opportunities.

        It orchestrates the process of fetching pain points, grouping them,
        scoring each group, and saving the resulting opportunities to the database.
        """
        logging.info("Generating opportunities...")
        try:
            if not self.pain_points:
                logging.warning("No pain points found in the database. Cannot generate opportunities.")
                return

            pain_point_groups = self._group_similar_pain_points()
            logging.info(f"Identified {len(pain_point_groups)} opportunity groups.")

            opportunities_to_save = []
            for group in track(pain_point_groups, description="Scoring opportunities..."):
                if len(group) < self.min_pain_points:
                    continue

                # For simplicity, use the longest pain point content as title/description
                title = max(group, key=lambda x: len(x['content']))['content'][:150]
                description = max(group, key=lambda x: len(x['content']))['content']
                
                # Take the most common category from the group
                categories = [pp['category'] for pp in group if pp['category']]
                if categories:
                    category = max(set(categories), key=categories.count)
                else:
                    category = "uncategorized"
                
                market_score = self._calculate_market_score(group)
                
                # A simple frequency score
                frequency_score = min(1.0, len(group) / 10.0)
                
                wtp_score = sum(self._detect_willingness_to_pay(pp['content']) for pp in group) / len(group)

                # Simple average of scores
                total_score = (market_score * 0.4 + frequency_score * 0.3 + wtp_score * 0.3)

                if total_score < self.min_score:
                    continue

                opportunities_to_save.append({
                    "title": title,
                    "description": description,
                    "category": category,
                    "market_score": market_score,
                    "frequency_score": frequency_score,
                    "willingness_to_pay_score": wtp_score,
                    "total_score": total_score,
                    "pain_point_count": len(group),
                    "pain_point_ids": json.dumps([pp['id'] for pp in group])
                })

            return opportunities_to_save

        except Exception as e:
            logging.error(f"An error occurred during opportunity generation: {e}", exc_info=True)
            return [] 