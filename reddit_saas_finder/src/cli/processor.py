"""Processes raw data for NLP analysis."""
import sqlite3
import logging
from datetime import datetime
from rich.progress import track

from reddit_saas_finder.src.data.database import DB_PATH
from reddit_saas_finder.src.nlp.pain_detector import PainDetector
from reddit_saas_finder.src.nlp.categorizer import Categorizer
from reddit_saas_finder.src.nlp.scorer import SentimentScorer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_pain_points():
    """
    Reads posts and comments from the database, processes them to find pain points,
    and saves the pain points back to the database.
    """
    logging.info("Starting pain point processing...")
    
    pain_detector = PainDetector()
    categorizer = Categorizer()
    scorer = SentimentScorer()

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Fetch all posts and comments
            cursor.execute("SELECT id, content, 'post' as type FROM posts WHERE content IS NOT NULL AND content != ''")
            posts = cursor.fetchall()
            cursor.execute("SELECT id, content, 'comment' as type FROM comments WHERE content IS NOT NULL AND content != ''")
            comments = cursor.fetchall()
            
            all_content = posts + comments
            logging.info(f"Processing {len(all_content)} documents.")

            pain_points_to_save = []
            for item in track(all_content, description="Analyzing content..."):
                pain_points = pain_detector.extract_pain_points(item['content'])
                for pp in pain_points:
                    category = categorizer.classify_problem_category(pp['content'])
                    severity = scorer.score_pain_point_severity(pp['content'])
                    pain_points_to_save.append((
                        item['id'],
                        item['type'],
                        pp['content'],
                        category,
                        severity,
                        0.85, # Placeholder for confidence_score
                        datetime.utcnow()
                    ))
            
            logging.info(f"Found {len(pain_points_to_save)} potential pain points.")

            if pain_points_to_save:
                cursor.executemany("""
                    INSERT INTO pain_points (source_id, source_type, content, category, severity_score, confidence_score, processed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, pain_points_to_save)
                conn.commit()
                logging.info(f"Saved {len(pain_points_to_save)} pain points to the database.")

    except sqlite3.Error as e:
        logging.error(f"Database error during pain point processing: {e}")
    except Exception as e:
        logging.error(f"An error occurred during pain point processing: {e}") 