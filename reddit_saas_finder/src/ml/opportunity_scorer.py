"""Scores opportunities using machine learning models."""
import sqlite3
import logging
import re
from datetime import datetime
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rich.progress import track

from reddit_saas_finder.src.data.database import get_pain_points, save_opportunities

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OpportunityScorer:
    """
    Generates and scores opportunities from processed pain points.
    """
    def __init__(self):
        # The db_path is no longer needed here as we use data access functions.
        pass

    def _group_similar_pain_points(self, pain_points, similarity_threshold=0.7):
        """
        Groups similar pain points together using TF-IDF and cosine similarity.
        """
        if not pain_points:
            return []

        # Extract content for vectorization
        contents = [pp['content'] for pp in pain_points]
        
        # Vectorize the text using TF-IDF
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(contents)
        
        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        groups = []
        visited = [False] * len(pain_points)
        
        for i in range(len(pain_points)):
            if visited[i]:
                continue
            
            # Start a new group with the current pain point
            current_group = [pain_points[i]]
            visited[i] = True
            
            # Find similar pain points
            for j in range(i + 1, len(pain_points)):
                if not visited[j] and similarity_matrix[i, j] >= similarity_threshold:
                    current_group.append(pain_points[j])
                    visited[j] = True
            
            groups.append(current_group)
            
        return groups

    def _calculate_market_score(self, pain_point_group):
        """
        Calculates market size score based on frequency, reach, and subreddit diversity.
        """
        frequency = len(pain_point_group)
        # Placeholder for unique_users and subreddit_diversity, needs more data
        unique_users = len(set(pp['source_id'] for pp in pain_point_group))
        subreddit_diversity = len(set(p['subreddit'] for p in pain_point_group if p['subreddit']))

        market_score = (frequency * 0.4 + unique_users * 0.4 + subreddit_diversity * 0.2) / 100
        return min(1.0, market_score)

    def _detect_willingness_to_pay(self, text):
        """
        Detects willingness to pay indicators in text.
        """
        pay_indicators = [
            r'\$\d+', r'budget', r'pay for', r'worth paying', r'subscription',
            r'premium', r'paid (tool|service|app)', r'enterprise'
        ]
        score = sum(0.2 for indicator in pay_indicators if re.search(indicator, text, re.IGNORECASE))
        return min(1.0, score)

    def generate_opportunities(self):
        """
        Main function to generate, score, and save opportunities.
        """
        logging.info("Generating opportunities...")
        try:
            pain_points = get_pain_points()

            if not pain_points:
                logging.warning("No pain points found in the database. Cannot generate opportunities.")
                return

            pain_point_groups = self._group_similar_pain_points(pain_points)
            logging.info(f"Identified {len(pain_point_groups)} opportunity groups.")

            opportunities_to_save = []
            for group in track(pain_point_groups, description="Scoring opportunities..."):
                # For simplicity, use the longest pain point content as title/description
                title = max(group, key=lambda x: len(x['content']))['content'][:150]
                description = max(group, key=lambda x: len(x['content']))['content']
                
                # Take category from the first item, assuming they are all the same
                category = group[0]['category'] if group[0]['category'] else "uncategorized"
                
                market_score = self._calculate_market_score(group)
                
                # A simple frequency score
                frequency_score = min(1.0, len(group) / 10.0)
                
                wtp_score = sum(self._detect_willingness_to_pay(pp['content']) for pp in group) / len(group)

                # Simple average of scores
                total_score = (market_score * 0.4 + frequency_score * 0.3 + wtp_score * 0.3)

                opportunities_to_save.append({
                    "title": title,
                    "description": description,
                    "category": category,
                    "market_score": market_score,
                    "frequency_score": frequency_score,
                    "willingness_to_pay_score": wtp_score,
                    "total_score": total_score,
                    "pain_point_count": len(group)
                })

            if opportunities_to_save:
                save_opportunities(opportunities_to_save)
                logging.info(f"Saved {len(opportunities_to_save)} new opportunities to the database.")

        except Exception as e:
            logging.error(f"An error occurred during opportunity generation: {e}", exc_info=True) 