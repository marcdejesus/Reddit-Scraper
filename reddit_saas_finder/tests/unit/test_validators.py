import pytest
import sqlite3
import pandas as pd
from utils.validators import DataValidator

@pytest.fixture
def db_connection():
    """Create an in-memory SQLite database for testing."""
    conn = sqlite3.connect(":memory:")
    # Create posts and comments tables
    conn.execute("""
        CREATE TABLE posts (
            id TEXT, title TEXT, subreddit TEXT, created_utc TEXT, author TEXT,
            content TEXT, score INTEGER, processed INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE comments (
            id TEXT, post_id TEXT, content TEXT, created_utc TEXT, author TEXT,
            score INTEGER, processed INTEGER
        )
    """)
    return conn

@pytest.fixture
def sample_data():
    """Create sample pandas DataFrames for posts and comments."""
    posts_data = [
        # Valid post
        ('p1', 'Valid Title', 'tech', 'time1', 'user1', 'This is a valid post content.', 10, 0),
        # Post with missing author
        ('p2', 'Missing Author', 'tech', 'time2', None, 'Content here.', 5, 0),
        # Duplicate post
        ('p3', 'Duplicate Post', 'tech', 'time3', 'user2', 'This is a duplicate.', 20, 0),
        ('p4', 'Duplicate Post', 'tech', 'time4', 'user3', 'This is a duplicate.', 25, 0),
        # Low quality (short content)
        ('p5', 'Short', 'tech', 'time5', 'user4', 'Too short', 15, 0)
    ]
    posts_df = pd.DataFrame(posts_data, columns=['id', 'title', 'subreddit', 'created_utc', 'author', 'content', 'score', 'processed'])

    comments_data = [
        # Valid comment
        ('c1', 'p1', 'This is a valid comment.', 'time_c1', 'user_c1', 10, 0),
        # Comment with missing content
        ('c2', 'p1', None, 'time_c2', 'user_c2', 5, 0),
        # Duplicate comment
        ('c3', 'p2', 'A duplicate comment.', 'time_c3', 'user_c3', 8, 0),
        ('c4', 'p3', 'A duplicate comment.', 'time_c4', 'user_c4', 9, 0),
        # Low quality (score < 1)
        ('c5', 'p4', 'This comment has a low score.', 'time_c5', 'user_c5', 0, 0)
    ]
    comments_df = pd.DataFrame(comments_data, columns=['id', 'post_id', 'content', 'created_utc', 'author', 'score', 'processed'])

    return posts_df, comments_df


def test_data_validator(db_connection, sample_data):
    """Test the DataValidator class logic."""
    posts_df, comments_df = sample_data
    posts_df.to_sql('posts', db_connection, if_exists='append', index=False)
    comments_df.to_sql('comments', db_connection, if_exists='append', index=False)

    validator = DataValidator(db_connection)
    validator.validate_data(min_post_length=10, min_comment_length=10)

    report = validator.report
    
    # Assertions for posts
    assert report['posts']['total'] == 5
    assert report['posts']['missing_critical_fields'] == 1 # p2 is missing author
    assert report['posts']['duplicates'] == 1 # p4 is a duplicate of p3
    assert report['posts']['spam_or_low_quality'] == 1 # p5 content is too short
    # Valid = Total - Missing - Duplicates - Spam
    # Valid = 5 - 1 - 1 - 1 = 2 (p1 is valid, p3 is not counted as invalid, but its duplicate p4 is)
    # The current logic is a bit tricky. Let's trace it.
    # Total = 5. Missing = 1. Duplicates = 1. Spam = 1 (p5).
    # The valid count is total - missing - duplicates - spam, so 5 - 1 - 1 - 1 = 2.
    # The current implementation of `validate_data` does not exclude rows from multiple categories.
    # A row can be both a duplicate and low quality, but it's counted in both.
    # Let's adjust the expected valid count based on the implementation.
    # The `valid` calculation in the source is:
    # `total_posts - missing_posts - duplicate_posts - spam_posts`
    # Let's verify the logic in the source.
    # `spam_posts` counts posts with short content OR low score. p5 is short.
    # `duplicate_posts` counts duplicated title/content. p4 is a duplicate of p3.
    # `missing_posts` counts missing critical fields. p2 has a null author.
    # So valid should be 5 - 1 - 1 - 1 = 2. This seems correct.
    assert report['posts']['valid'] == 2

    # Assertions for comments
    assert report['comments']['total'] == 5
    assert report['comments']['missing_critical_fields'] == 1 # c2 has null content
    assert report['comments']['duplicates'] == 1 # c4 is a duplicate of c3
    assert report['comments']['spam_or_low_quality'] == 1 # c5 has score < 1
    assert report['comments']['valid'] == 2 