"""Manages interaction with the Reddit API via PRAW."""
import praw
from rich.console import Console
from datetime import datetime
from typing import List, Dict, Any
import logging

from utils.config import ConfigManager
from data.database import save_posts_and_comments

console = Console()
logging.basicConfig(filename='reddit_client.log', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class RedditClient:
    """
    Manages all interactions with the Reddit API using the PRAW library.

    This class handles the authentication with Reddit, fetching posts and comments,
    and coordinating with the database module to save the scraped data.
    """
    def __init__(self):
        """
        Initializes the RedditClient.

        It fetches API credentials from the configuration and sets up a PRAW instance.
        Raises:
            ValueError: If Reddit API credentials are not found in the configuration.
        """
        config_manager = ConfigManager()
        client_id, client_secret, user_agent = config_manager.get_reddit_credentials()
        
        if not all([client_id, client_secret, user_agent]):
            console.print("[bold red]Missing Reddit API credentials in config or environment.[/bold red]")
            raise ValueError("Missing Reddit API credentials.")

        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.data_collection_config = config_manager.get_data_collection_config()
        console.print("RedditClient initialized successfully.", style="green")

    def scrape_subreddit(self, subreddit_name: str, time_filter: str = 'week', limit: int = 100) -> None:
        """
        Scrapes posts and their top comments from a given subreddit.

        The scraped data is then passed to the database module for storage.

        Args:
            subreddit_name (str): The name of the subreddit to scrape (e.g., 'SaaS').
            time_filter (str, optional): The time filter for sorting top posts
                ('all', 'year', 'month', 'week', 'day'). Defaults to 'week'.
            limit (int, optional): The maximum number of posts to scrape. Defaults to 100.
        """
        console.print(f"Scraping r/{subreddit_name} (time: {time_filter}, limit: {limit})...", style="bold blue")
        subreddit = self.reddit.subreddit(subreddit_name)
        posts_data = []
        comments_data = []
        
        try:
            for post in subreddit.top(time_filter=time_filter, limit=limit):
                posts_data.append({
                    'id': post.id,
                    'subreddit': post.subreddit.display_name,
                    'title': post.title,
                    'selftext': post.selftext,
                    'author': getattr(post.author, 'name', '[deleted]'),
                    'score': post.score,
                    'num_comments': post.num_comments,
                    'created_utc': post.created_utc,
                    'url': post.url,
                    'link_flair_text': post.link_flair_text,
                    'is_self': post.is_self,
                    'upvote_ratio': post.upvote_ratio,
                })

                post.comments.replace_more(limit=0)
                max_comments = self.data_collection_config.get('max_comments_per_post', 100)
                for comment in post.comments.list()[:max_comments]:
                    comments_data.append({
                        'id': comment.id,
                        'post_id': comment.submission.id,
                        'body': comment.body,
                        'author': getattr(comment.author, 'name', '[deleted]'),
                        'score': comment.score,
                        'created_utc': comment.created_utc,
                        'parent_id': comment.parent_id,
                        'depth': comment.depth,
                        'is_submitter': comment.is_submitter,
                    })
            
            console.print(f"Scraped {len(posts_data)} posts and {len(comments_data)} comments from r/{subreddit_name}.")
            
            if posts_data or comments_data:
                save_posts_and_comments(posts_data, comments_data)

        except Exception as e:
            console.print(f"An error occurred while scraping r/{subreddit_name}: {e}", style="bold red")
            logging.error(f"Error scraping r/{subreddit_name}: {e}", exc_info=True)

    # The save_to_database method is removed, as saving is now handled by the scrape_subreddit method directly
    # by calling the dedicated function in database.py. This improves separation of concerns. 