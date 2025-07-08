import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from rich.console import Console
import typer

console = Console()

# --- Database Setup ---
# Correctly locate the project root to build the DB path
# This assumes database.py is in src/data/
DB_FILE_PATH = os.path.abspath(__file__)
SRC_DIR = os.path.dirname(os.path.dirname(DB_FILE_PATH))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
DB_DIR = os.path.join(PROJECT_ROOT, "data")
DB_PATH = os.path.join(DB_DIR, "reddit_data.db")

# --- Data Models ---
class Post:
    """Represents a Reddit post."""
    def __init__(self, id: str, subreddit: str, title: str, content: Optional[str], author: Optional[str], score: int, num_comments: int, created_utc: float, url: str, flair: Optional[str], is_self: bool, upvote_ratio: float, processed: bool = False, **kwargs):
        """Initializes a Post object.

        Args:
            id (str): The unique ID of the post.
            subreddit (str): The subreddit the post belongs to.
            title (str): The title of the post.
            content (Optional[str]): The text content of the post.
            author (Optional[str]): The author of the post.
            score (int): The score of the post.
            num_comments (int): The number of comments on the post.
            created_utc (float): The UTC timestamp of when the post was created.
            url (str): The URL of the post.
            flair (Optional[str]): The flair of the post.
            is_self (bool): Whether the post is a self-post.
            upvote_ratio (float): The upvote ratio of the post.
            processed (bool): Whether the post has been processed.
        """
        self.id = id
        self.subreddit = subreddit
        self.title = title
        self.content = content
        self.author = author
        self.score = score
        self.num_comments = num_comments
        self.created_utc = datetime.fromisoformat(created_utc) if isinstance(created_utc, str) else datetime.fromtimestamp(created_utc)
        self.url = url
        self.flair = flair
        self.is_self = is_self
        self.upvote_ratio = upvote_ratio
        self.processed = bool(processed)

class Comment:
    """Represents a Reddit comment."""
    def __init__(self, id: str, post_id: str, content: str, author: Optional[str], score: int, created_utc: float, parent_id: str, depth: int, is_submitter: bool, processed: bool = False, **kwargs):
        """Initializes a Comment object.

        Args:
            id (str): The unique ID of the comment.
            post_id (str): The ID of the post the comment belongs to.
            content (str): The text content of the comment.
            author (Optional[str]): The author of the comment.
            score (int): The score of the comment.
            created_utc (float): The UTC timestamp of when the comment was created.
            parent_id (str): The ID of the parent comment or post.
            depth (int): The depth of the comment in the thread.
            is_submitter (bool): Whether the comment author is the post submitter.
            processed (bool): Whether the comment has been processed.
        """
        self.id = id
        self.post_id = post_id
        self.content = content
        self.author = author
        self.score = score
        self.created_utc = datetime.fromisoformat(created_utc) if isinstance(created_utc, str) else datetime.fromtimestamp(created_utc)
        self.parent_id = parent_id
        self.depth = depth
        self.is_submitter = is_submitter
        self.processed = bool(processed)

class PainPoint:
    """Represents a pain point extracted from a post or comment."""
    def __init__(self, source_id: str, source_type: str, content: str, category: Optional[str] = None, **kwargs):
        """Initializes a PainPoint object.

        Args:
            source_id (str): The ID of the source post or comment.
            source_type (str): The type of the source ('post' or 'comment').
            content (str): The text content of the pain point.
        """
        self.source_id = source_id
        self.source_type = source_type
        self.content = content
        # These will be populated by the NLP pipeline
        self.category: Optional[str] = category
        self.severity_score: Optional[float] = kwargs.get('severity_score')
        self.confidence_score: Optional[float] = kwargs.get('confidence_score')
        self.sentiment_score: Optional[float] = kwargs.get('sentiment_score')
        self.keywords: Optional[str] = kwargs.get('keywords') # Stored as JSON string
        self.processed_at: datetime = datetime.utcnow()
        self.subreddit: Optional[str] = kwargs.get('subreddit')
        self.engagement_score: Optional[float] = kwargs.get('engagement_score')

class Opportunity:
    """Represents a potential SaaS opportunity."""
    def __init__(self, id: int, title: str, description: str, category: str, total_score: float, pain_point_count: int, **kwargs):
        """Initializes an Opportunity object.

        Args:
            id (int): The unique ID of the opportunity.
            title (str): The title of the opportunity.
            description (str): The description of the opportunity.
            category (str): The category of the opportunity.
            total_score (float): The total score of the opportunity.
            pain_point_count (int): The number of pain points associated with the opportunity.
        """
        self.id = id
        self.title = title
        self.description = description
        self.category = category
        self.total_score = total_score
        self.pain_point_count = pain_point_count
        self.market_score: float = kwargs.get('market_score', 0.0)
        self.pain_point_ids: str = kwargs.get('pain_point_ids', '[]')


# --- Schema Definitions ---
POSTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id TEXT PRIMARY KEY,
    subreddit TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    author TEXT,
    score INTEGER,
    num_comments INTEGER,
    created_utc TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    url TEXT,
    flair TEXT,
    is_self BOOLEAN,
    upvote_ratio REAL,
    processed BOOLEAN DEFAULT 0
);
"""

COMMENTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS comments (
    id TEXT PRIMARY KEY,
    post_id TEXT REFERENCES posts(id),
    content TEXT NOT NULL,
    author TEXT,
    score INTEGER,
    created_utc TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parent_id TEXT,
    depth INTEGER,
    is_submitter BOOLEAN,
    processed BOOLEAN DEFAULT 0
);
"""

PAIN_POINTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS pain_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    source_type TEXT NOT NULL, -- 'post' or 'comment'
    content TEXT NOT NULL,
    category TEXT,
    severity_score REAL,
    confidence_score REAL,
    sentiment_score REAL,
    keywords TEXT, -- Stored as a JSON array string
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subreddit TEXT,
    engagement_score REAL
);
"""

OPPORTUNITIES_SCHEMA = """
CREATE TABLE IF NOT EXISTS opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    market_score REAL, -- Renamed from market_size_score for simplicity
    frequency_score REAL,
    willingness_to_pay_score REAL,
    total_score REAL,
    pain_point_count INTEGER,
    pain_point_ids TEXT, -- JSON array of pain point IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def create_indexes(connection):
    """Creates indexes on frequently queried columns to improve performance."""
    cursor = connection.cursor()
    console.print("Creating database indexes for performance...")
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_processed ON posts(processed);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_processed ON comments(processed);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id);")
        connection.commit()
        console.print("[bold green]Database indexes created successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error creating indexes: {e}[/bold red]")
        connection.rollback()
    finally:
        cursor.close()

def get_db_connection(db_path: str = DB_PATH):
    """Establishes a connection to the SQLite database.

    Args:
        db_path (str, optional): The path to the database file. 
            Defaults to DB_PATH.

    Returns:
        sqlite3.Connection: A connection object to the database.
    """
    if db_path != ":memory:":
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database(connection=None):
    """Initializes the database by creating tables if they don't exist."""
    close_conn = False
    if connection is None:
        connection = get_db_connection()
        close_conn = True

    if connection is None:
        return  # Stop if connection failed

    try:
        cursor = connection.cursor()
        cursor.execute(POSTS_SCHEMA)
        cursor.execute(COMMENTS_SCHEMA)
        cursor.execute(PAIN_POINTS_SCHEMA)
        cursor.execute(OPPORTUNITIES_SCHEMA)
        connection.commit()
        console.print("[bold green]Database tables are set up.[/bold green]")
        
        # Create indexes for performance
        create_indexes(connection)

    except sqlite3.Error as e:
        console.print(f"[bold red]Database error: {e}[/bold red]")
    finally:
        if close_conn and connection:
            connection.close()


# --- Data Access Functions ---

def save_posts_and_comments(posts: List[Dict[str, Any]], comments: List[Dict[str, Any]]):
    """Saves posts and their corresponding comments to the database in a single transaction.

    This function performs a bulk `INSERT OR IGNORE` operation, so existing records
    are not updated.

    Args:
        posts (List[Dict[str, Any]]): A list of dictionaries, each representing a post.
        comments (List[Dict[str, Any]]): A list of dictionaries, each representing a comment.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Insert posts
        post_data = [(p['id'], p['subreddit'], p['title'], p.get('selftext', ''), p['author'], p['score'], p['num_comments'], datetime.fromtimestamp(p['created_utc']), p['url'], p.get('link_flair_text'), p['is_self'], p['upvote_ratio']) for p in posts]
        cursor.executemany("INSERT OR IGNORE INTO posts (id, subreddit, title, content, author, score, num_comments, created_utc, url, flair, is_self, upvote_ratio) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", post_data)
        
        # Insert comments
        comment_data = [(c['id'], c['post_id'], c['body'], c.get('author'), c['score'], datetime.fromtimestamp(c['created_utc']), c['parent_id'], c['depth'], c['is_submitter']) for c in comments]
        cursor.executemany("INSERT OR IGNORE INTO comments (id, post_id, content, author, score, created_utc, parent_id, depth, is_submitter) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", comment_data)
        
        conn.commit()
        console.print(f"Saved {cursor.rowcount} new items to the database.")

def get_unprocessed_posts() -> List[Post]:
    """Fetches all posts from the database that have not yet been processed.

    Returns:
        List[Post]: A list of Post objects.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts WHERE processed = 0")
        return [Post(**row) for row in cursor.fetchall()]

def get_unprocessed_comments() -> List[Comment]:
    """Fetches all comments from the database that have not yet been processed.

    Returns:
        List[Comment]: A list of Comment objects.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM comments WHERE processed = 0")
        return [Comment(**row) for row in cursor.fetchall()]

def save_pain_points(pain_points: List[PainPoint]):
    """Saves a list of pain points to the database."""
    if not pain_points:
        return

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Prepare data for bulk insertion
        pain_point_data = [
            (
                pp.source_id,
                pp.source_type,
                pp.content,
                pp.category,
                pp.severity_score,
                pp.confidence_score,
                pp.sentiment_score,
                pp.keywords,
                pp.subreddit,
                pp.engagement_score,
            )
            for pp in pain_points
        ]
        
        insert_query = """
        INSERT INTO pain_points (
            source_id, source_type, content, category, severity_score, 
            confidence_score, sentiment_score, keywords, subreddit, engagement_score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        
        cursor.executemany(insert_query, pain_point_data)
        conn.commit()
    except sqlite3.Error as e:
        console.print(f"[bold red]Database error saving pain points: {e}[/bold red]")
        conn.rollback()
    finally:
        conn.close()


def get_pain_points() -> List[Dict[str, Any]]:
    """Retrieves all pain points from the database.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary
            represents a pain point.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pain_points")
        return [dict(row) for row in cursor.fetchall()]

def save_opportunities(opportunities: List[Dict[str, Any]]):
    """Saves a list of opportunity dictionaries to the database.

    Args:
        opportunities (List[Dict[str, Any]]): A list of dictionaries, each
            representing an opportunity.
    """
    opp_data = [(o['title'], o['description'], o['category'], o.get('market_score', 0), o['frequency_score'], o['willingness_to_pay_score'], o['total_score'], o['pain_point_count'], o.get('pain_point_ids', '[]')) for o in opportunities]
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany("INSERT INTO opportunities (title, description, category, market_score, frequency_score, willingness_to_pay_score, total_score, pain_point_count, pain_point_ids) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", opp_data)
        conn.commit()

def get_opportunities(limit: int = 20) -> List[Opportunity]:
    """Retrieves opportunities from the database, ordered by total score.

    Args:
        limit (int, optional): The maximum number of opportunities to retrieve.
            Defaults to 20.

    Returns:
        List[Opportunity]: A list of Opportunity objects.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM opportunities ORDER BY total_score DESC LIMIT ?", (limit,))
        return [Opportunity(**row) for row in cursor.fetchall()]

def get_category_distribution() -> List[Tuple[str, int]]:
    """Gets the distribution of opportunities across different categories.

    Returns:
        List[Tuple[str, int]]: A list of tuples, where each tuple contains
            a category name and the count of opportunities in that category.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT category, COUNT(*) FROM opportunities GROUP BY category")
        return cursor.fetchall()

def get_subreddit_for_post(post_id: str) -> Optional[str]:
    """Gets the subreddit for a given post ID.

    Args:
        post_id (str): The ID of the post.

    Returns:
        Optional[str]: The name of the subreddit, or None if not found.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT subreddit FROM posts WHERE id = ?", (post_id,))
        result = cursor.fetchone()
        return result['subreddit'] if result else None 