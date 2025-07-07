"""Manages interaction with the Reddit API via PRAW."""
import praw
import sqlite3
import logging
from datetime import datetime

from reddit_saas_finder.src.utils.config import ConfigManager
from reddit_saas_finder.src.data.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RedditClient:
    def __init__(self):
        """
        Initializes the RedditClient with API credentials from the config.
        """
        config_manager = ConfigManager()
        client_id, client_secret, user_agent = config_manager.get_reddit_credentials()
        
        if not all([client_id, client_secret, user_agent]):
            raise ValueError("Missing Reddit API credentials in config.")

        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.db_path = config_manager.get_database_path()
        self.data_collection_config = config_manager.get_data_collection_config()
        logging.info("RedditClient initialized successfully.")

    def scrape_subreddit(self, subreddit_name: str, time_filter: str = 'week', limit: int = 100):
        """
        Scrapes posts and their top comments from a given subreddit.
        """
        logging.info(f"Scraping subreddit '{subreddit_name}' with time_filter='{time_filter}' and limit={limit}.")
        subreddit = self.reddit.subreddit(subreddit_name)
        posts_data = []
        comments_data = []
        
        try:
            for post in subreddit.top(time_filter=time_filter, limit=limit):
                posts_data.append({
                    'id': post.id,
                    'subreddit': post.subreddit.display_name,
                    'title': post.title,
                    'content': post.selftext,
                    'author': post.author.name if post.author else '[deleted]',
                    'score': post.score,
                    'num_comments': post.num_comments,
                    'created_utc': datetime.utcfromtimestamp(post.created_utc),
                    'scraped_at': datetime.utcnow()
                })

                # Fetch comments
                post.comments.replace_more(limit=0) # Remove "load more comments" links
                max_comments = self.data_collection_config.get('max_comments_per_post', 100)
                for comment in post.comments.list()[:max_comments]:
                    comments_data.append({
                        'id': comment.id,
                        'post_id': post.id,
                        'content': comment.body,
                        'author': comment.author.name if comment.author else '[deleted]',
                        'score': comment.score,
                        'created_utc': datetime.utcfromtimestamp(comment.created_utc),
                        'scraped_at': datetime.utcnow()
                    })
            logging.info(f"Scraped {len(posts_data)} posts and {len(comments_data)} comments from '{subreddit_name}'.")
            return posts_data, comments_data
        except Exception as e:
            logging.error(f"An error occurred while scraping '{subreddit_name}': {e}")
            return [], []

    def save_to_database(self, posts, comments):
        """
        Saves scraped posts and comments to the SQLite database.
        """
        if not posts and not comments:
            logging.info("No new data to save to the database.")
            return

        logging.info(f"Saving {len(posts)} posts and {len(comments)} comments to the database.")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Use INSERT OR REPLACE to avoid duplicates and update existing entries
                posts_to_insert = [tuple(p.values()) for p in posts]
                cursor.executemany("""
                    INSERT OR REPLACE INTO posts (id, subreddit, title, content, author, score, num_comments, created_utc, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, posts_to_insert)

                comments_to_insert = [tuple(c.values()) for c in comments]
                cursor.executemany("""
                    INSERT OR REPLACE INTO comments (id, post_id, content, author, score, created_utc, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, comments_to_insert)
                
                conn.commit()
                logging.info("Data saved to database successfully.")
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}") 