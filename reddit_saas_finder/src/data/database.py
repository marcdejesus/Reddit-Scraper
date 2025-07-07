import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from rich.console import Console

console = Console()

# --- Database Setup ---
DB_DIR = "reddit_saas_finder/data"
DB_PATH = os.path.join(DB_DIR, "reddit_data.db")

# --- Data Models ---
# These classes represent the data structures for our application, matching the database schema.
class Post:
    def __init__(self, id: str, subreddit: str, title: str, content: Optional[str], author: Optional[str], score: int, num_comments: int, created_utc: float, url: str, flair: Optional[str], is_self: bool, upvote_ratio: float, processed: bool = False, **kwargs):
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
    def __init__(self, id: str, post_id: str, content: str, author: Optional[str], score: int, created_utc: float, parent_id: str, depth: int, is_submitter: bool, processed: bool = False, **kwargs):
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
    def __init__(self, source_id: str, source_type: str, content: str, **kwargs):
        self.source_id = source_id
        self.source_type = source_type
        self.content = content
        # These will be populated by the NLP pipeline
        self.category: Optional[str] = kwargs.get('category')
        self.severity_score: Optional[float] = kwargs.get('severity_score')
        self.confidence_score: Optional[float] = kwargs.get('confidence_score')
        self.sentiment_score: Optional[float] = kwargs.get('sentiment_score')
        self.keywords: Optional[str] = kwargs.get('keywords') # Stored as JSON string
        self.processed_at: datetime = datetime.utcnow()
        self.subreddit: Optional[str] = kwargs.get('subreddit')
        self.engagement_score: Optional[float] = kwargs.get('engagement_score')

class Opportunity:
    def __init__(self, id: int, title: str, description: str, category: str, total_score: float, pain_point_count: int, **kwargs):
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

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initializes the database and creates tables."""
    console.print(f"Initializing database at [cyan]{DB_PATH}[/cyan]...")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(POSTS_SCHEMA)
        cursor.execute(COMMENTS_SCHEMA)
        cursor.execute(PAIN_POINTS_SCHEMA)
        cursor.execute(OPPORTUNITIES_SCHEMA)
        conn.commit()
    console.print("[green]Database initialized successfully.[/green]")

# --- Data Access Functions ---

def save_posts_and_comments(posts: List[Dict[str, Any]], comments: List[Dict[str, Any]]):
    """Saves posts and comments to the database, ignoring duplicates."""
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
    """Fetches all posts that have not been processed yet."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts WHERE processed = 0")
        return [Post(**row) for row in cursor.fetchall()]

def get_unprocessed_comments() -> List[Comment]:
    """Fetches all comments that have not been processed yet."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM comments WHERE processed = 0")
        return [Comment(**row) for row in cursor.fetchall()]

def save_pain_points(pain_points: List[PainPoint]):
    """Saves a list of PainPoint objects to the database and marks sources as processed."""
    if not pain_points:
        return
        
    pp_data = [(pp.source_id, pp.source_type, pp.content, pp.category, pp.severity_score, pp.confidence_score, pp.sentiment_score, pp.keywords, pp.subreddit, pp.engagement_score) for pp in pain_points]
    
    post_ids_to_mark = [pp.source_id for pp in pain_points if pp.source_type == 'post']
    comment_ids_to_mark = [pp.source_id for pp in pain_points if pp.source_type == 'comment']
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany("INSERT INTO pain_points (source_id, source_type, content, category, severity_score, confidence_score, sentiment_score, keywords, subreddit, engagement_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", pp_data)
        
        if post_ids_to_mark:
            placeholders = ', '.join('?' for _ in post_ids_to_mark)
            cursor.execute(f"UPDATE posts SET processed = 1 WHERE id IN ({placeholders})", post_ids_to_mark)
        if comment_ids_to_mark:
            placeholders = ', '.join('?' for _ in comment_ids_to_mark)
            cursor.execute(f"UPDATE comments SET processed = 1 WHERE id IN ({placeholders})", comment_ids_to_mark)
            
        conn.commit()

def get_pain_points() -> List[Dict[str, Any]]:
    """Retrieves all pain points from the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pain_points")
        return [dict(row) for row in cursor.fetchall()]

def save_opportunities(opportunities: List[Dict[str, Any]]):
    """Saves a list of opportunity dictionaries to the database."""
    opp_data = [(o['title'], o['description'], o['category'], o.get('market_score', 0), o['frequency_score'], o['willingness_to_pay_score'], o['total_score'], o['pain_point_count'], o.get('pain_point_ids', '[]')) for o in opportunities]
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany("INSERT INTO opportunities (title, description, category, market_score, frequency_score, willingness_to_pay_score, total_score, pain_point_count, pain_point_ids) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", opp_data)
        conn.commit()

def get_opportunities(limit: int = 20) -> List[Opportunity]:
    """Retrieves opportunities from the database, ordered by score."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM opportunities ORDER BY total_score DESC LIMIT ?", (limit,))
        return [Opportunity(**row) for row in cursor.fetchall()]

def get_category_distribution() -> List[Tuple[str, int]]:
    """Calculates the distribution of opportunities across categories."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT category, COUNT(*) as count FROM opportunities GROUP BY category ORDER BY count DESC")
        return [(row['category'], row['count']) for row in cursor.fetchall()] 