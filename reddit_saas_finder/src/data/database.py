import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Define the path for the database relative to the project's root directory
DB_DIR = "reddit_saas_finder/data"
DB_PATH = os.path.join(DB_DIR, "reddit_data.db")

POSTS_SCHEMA = """
CREATE TABLE posts (
    id TEXT PRIMARY KEY,
    subreddit TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    author TEXT,
    score INTEGER,
    num_comments INTEGER,
    created_utc TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

COMMENTS_SCHEMA = """
CREATE TABLE comments (
    id TEXT PRIMARY KEY,
    post_id TEXT REFERENCES posts(id),
    content TEXT NOT NULL,
    author TEXT,
    score INTEGER,
    created_utc TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

PAIN_POINTS_SCHEMA = """
CREATE TABLE pain_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    source_type TEXT NOT NULL, -- 'post' or 'comment'
    content TEXT NOT NULL,
    category TEXT,
    severity_score REAL,
    confidence_score REAL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

OPPORTUNITIES_SCHEMA = """
CREATE TABLE opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    market_score REAL,
    frequency_score REAL,
    willingness_to_pay_score REAL,
    total_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

class Post:
    def __init__(self, id, title, content):
        self.id = id
        self.title = title
        self.content = content

class Comment:
    def __init__(self, id, content):
        self.id = id
        self.content = content

class PainPoint:
    def __init__(self, source_id, source_type, content, severity_score, confidence_score):
        self.source_id = source_id
        self.source_type = source_type
        self.content = content
        self.severity_score = severity_score
        self.confidence_score = confidence_score

class Opportunity:
    def __init__(self, id, title, category, total_score, pain_point_count):
        self.id = id
        self.title = title
        self.category = category
        self.total_score = total_score
        self.pain_point_count = pain_point_count

def initialize_database():
    """
    Initializes the SQLite database and creates the necessary tables
    if the database file does not already exist.
    """
    if os.path.exists(DB_PATH):
        print(f"Database already exists at {DB_PATH}")
        return

    # Create the data directory if it doesn't exist
    os.makedirs(DB_DIR, exist_ok=True)

    print(f"Initializing database at {DB_PATH}...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("Creating tables...")
        cursor.execute(POSTS_SCHEMA)
        cursor.execute(COMMENTS_SCHEMA)
        cursor.execute(PAIN_POINTS_SCHEMA)
        cursor.execute(OPPORTUNITIES_SCHEMA)

        conn.commit()
        print("Tables created successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

def get_unprocessed_posts() -> List[Post]:
    # This is a mock implementation.
    # In a real scenario, you would query the database for posts that haven't been processed.
    return [Post(id="post1", title="Test Post", content="This is some content.")]

def get_unprocessed_comments() -> List[Comment]:
    # This is a mock implementation.
    return [Comment(id="comment1", content="This is a test comment.")]

def save_pain_points(pain_points: List[PainPoint]):
    # This is a mock implementation.
    print(f"Saving {len(pain_points)} pain points.")
    pass

def get_pain_points() -> List[Dict[str, Any]]:
    # Mock implementation
    return [{"content": "This is a pain point", "category": "productivity", "total_score": 0.8, "pain_point_count": 1, "title": "Great Opportunity", "description": "A great opportunity"}]

def save_opportunities(opportunities: List[Opportunity]):
    # This is a mock implementation.
    print(f"Saving {len(opportunities)} opportunities.")
    pass

def get_opportunities(limit: int) -> List[Opportunity]:
    # Mock implementation
    return [Opportunity(id=1, title="Test Opportunity", category="productivity", total_score=0.9, pain_point_count=5)]

def get_category_distribution() -> List[Tuple[str, int]]:
    # Mock implementation
    return [("productivity", 10), ("communication", 5)] 