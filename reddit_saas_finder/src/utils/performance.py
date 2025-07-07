
import pickle
import hashlib
import os
from rich.console import Console

console = Console()
CACHE_DIR = "reddit_saas_finder/cache"

class PerformanceOptimizer:
    """
    Provides caching and batch processing functionalities to improve performance.
    """
    def __init__(self):
        os.makedirs(CACHE_DIR, exist_ok=True)

    def get_cached_nlp_result(self, text: str) -> any:
        """
        Retrieves a cached NLP result for the given text.
        """
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_file = os.path.join(CACHE_DIR, f"{text_hash}.pkl")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                console.log(f"Cache hit for hash: {text_hash}")
                return pickle.load(f)
        return None

    def cache_nlp_result(self, text: str, result: any):
        """
        Caches the NLP result for the given text.
        """
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_file = os.path.join(CACHE_DIR, f"{text_hash}.pkl")
        
        with open(cache_file, 'wb') as f:
            pickle.dump(result, f)

    def clear_cache(self):
        """
        Clears all cached NLP results.
        """
        for filename in os.listdir(CACHE_DIR):
            file_path = os.path.join(CACHE_DIR, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        console.print("[bold green]NLP cache cleared.[/bold green]")

    def batch_process_pain_points(self, batch_size: int = 100):
        """
        Processes unprocessed posts and comments in batches.
        This is a placeholder and should be integrated with the actual NLP processor.
        """
        from data.database import get_unprocessed_posts, get_unprocessed_comments, save_pain_points, get_subreddit_for_post
        from nlp.pain_detector import AdvancedPainDetector

        console.print(f"Starting batch processing with batch size: {batch_size}")

        pain_detector = AdvancedPainDetector()

        # Process posts
        unprocessed_posts = get_unprocessed_posts()
        for i in range(0, len(unprocessed_posts), batch_size):
            batch = unprocessed_posts[i:i + batch_size]
            console.log(f"Processing post batch {i//batch_size + 1}...")
            pain_points = []
            for post in batch:
                if post.content:
                    detected = pain_detector.extract_pain_points(post.content)
                    for pp in detected:
                        pp['source_id'] = post.id
                        pp['source_type'] = 'post'
                        pp['subreddit'] = post.subreddit
                    pain_points.extend(detected)
            if pain_points:
                save_pain_points(pain_points)

        # Process comments
        unprocessed_comments = get_unprocessed_comments()
        for i in range(0, len(unprocessed_comments), batch_size):
            batch = unprocessed_comments[i:i + batch_size]
            console.log(f"Processing comment batch {i//batch_size + 1}...")
            pain_points = []
            for comment in batch:
                if comment.content:
                    detected = pain_detector.extract_pain_points(comment.content)
                    subreddit = get_subreddit_for_post(comment.post_id)
                    for pp in detected:
                        pp['source_id'] = comment.id
                        pp['source_type'] = 'comment'
                        pp['subreddit'] = subreddit if subreddit else "unknown"
                    pain_points.extend(detected)
            if pain_points:
                save_pain_points(pain_points)
        
        console.print("[bold green]Batch processing complete.[/bold green]") 