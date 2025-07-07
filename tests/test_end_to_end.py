import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
import os
import csv
from pathlib import Path
import tempfile
import shutil
import sqlite3

# Adjust the path to import the app from the correct location
from cli.main import app
from data.database import get_db_connection, initialize_database

runner = CliRunner()

@pytest.fixture(scope="function")
def test_db():
    """Fixture to set up an in-memory SQLite database for testing."""
    connection = get_db_connection(":memory:")
    initialize_database(connection)
    
    # We need a mock that acts as a context manager but doesn't close our single connection.
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = connection
    mock_cm.__exit__.return_value = None

    with patch('data.database.get_db_connection') as mock_get_conn:
        mock_get_conn.return_value = mock_cm
        yield connection

    connection.close()

@pytest.fixture(scope="module")
def mock_praw():
    """Fixture to mock the PRAW Reddit API client."""
    with patch('praw.Reddit') as mock_reddit:
        # Mocking comments
        mock_comment = MagicMock()
        mock_comment.id = "comment_id"
        mock_comment.body = "This is a test comment."
        mock_comment.author = MagicMock()
        mock_comment.author.name = "commenter"
        mock_comment.score = 5
        mock_comment.created_utc = 1672531200
        mock_comment.parent_id = "t3_test_id"
        mock_comment.depth = 1
        mock_comment.is_submitter = False
        
        # Mocking subreddit and its submissions
        mock_submission = MagicMock()
        mock_submission.id = "test_id"
        mock_submission.title = "Test Post"
        mock_submission.selftext = "This is the content of the test post. It is so frustrating."
        mock_submission.author = MagicMock()
        mock_submission.author.name = "test_author"
        mock_submission.score = 10
        mock_submission.num_comments = 5
        mock_submission.created_utc = 1672531200
        mock_submission.url = "http://test.url/post"
        mock_submission.link_flair_text = "test_flair"
        mock_submission.is_self = True
        mock_submission.upvote_ratio = 0.9
        
        mock_submission.subreddit = MagicMock()
        mock_submission.subreddit.display_name = "test"
        
        mock_comment.submission = mock_submission

        mock_comments = MagicMock()
        mock_comments.list.return_value = [mock_comment]
        mock_submission.comments = mock_comments

        mock_subreddit = MagicMock()
        mock_subreddit.top.return_value = [mock_submission] * 5
        
        mock_reddit_instance = MagicMock()
        mock_reddit_instance.subreddit.return_value = mock_subreddit
        
        mock_reddit.return_value = mock_reddit_instance
        yield mock_reddit

@pytest.fixture
def mock_keyword_manager():
    """Fixture to mock the KeywordManager."""
    with patch('nlp.pain_detector.KeywordManager') as mock_manager:
        mock_instance = mock_manager.return_value
        mock_instance.get_pain_point_keywords.return_value = ["frustrating", "difficult"]
        yield mock_instance

def test_init_db(test_db):
    """Test the init-db command."""
    result = runner.invoke(app, ["init-db"])
    assert result.exit_code == 0
    assert "Database initialized successfully" in result.stdout

def test_scrape_command(test_db, mock_praw):
    """Test the scrape command with mocked Reddit API."""
    result = runner.invoke(app, ["scrape", "subreddit", "--name", "test", "--limit", "5"])
    assert result.exit_code == 0
    assert "Scraping task for r/test completed." in result.stdout
    
    # Verify data was inserted
    cursor = test_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM posts")
    assert cursor.fetchone()[0] > 0

def test_process_command(test_db, mock_praw, mock_keyword_manager):
    """Test the process command."""
    # First, ensure there's data to process by running scrape
    runner.invoke(app, ["scrape", "subreddit", "--name", "test", "--limit", "5"])
    
    result = runner.invoke(app, ["process", "pain-points"])
    assert result.exit_code == 0
    assert "Pain point processing completed successfully." in result.stdout

def test_opportunities_command(test_db, mock_praw, mock_keyword_manager):
    """Test the opportunities command."""
    # Ensure data is scraped and processed first
    runner.invoke(app, ["scrape", "subreddit", "--name", "test", "--limit", "5"])
    runner.invoke(app, ["process", "pain-points"])

    result = runner.invoke(app, ["opportunities", "generate"])
    assert result.exit_code == 0
    assert "Opportunity generation completed successfully." in result.stdout

def test_show_command(test_db, mock_praw, mock_keyword_manager):
    """Test the show command for opportunities."""
    # Ensure opportunities are generated
    runner.invoke(app, ["scrape", "subreddit", "--name", "test", "--limit", "5"])
    result = runner.invoke(app, ["process", "pain-points"])
    runner.invoke(app, ["opportunities", "generate"])
    
    result = runner.invoke(app, ["opportunities", "show"])
    assert result.exit_code == 0
    # Check for table headers in the output
    assert "Title" in result.stdout
    assert "Score" in result.stdout

def test_export_command(test_db, mock_praw, mock_keyword_manager):
    """Test the export command for opportunities."""
    # Ensure opportunities are generated
    runner.invoke(app, ["scrape", "subreddit", "--name", "test", "--limit", "5"])
    runner.invoke(app, ["process", "pain-points"])
    runner.invoke(app, ["opportunities", "generate"])

    # Create a temporary directory for the export
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch('cli.export.exporter.export_dir', tmpdir):
            result = runner.invoke(app, ["export", "export", "--opportunities", "--format", "csv"])
            assert result.exit_code == 0
            assert "Successfully exported opportunities" in result.stdout

            # Verify the file was created
            exported_files = list(Path(tmpdir).glob("opportunities_*.csv"))
            assert len(exported_files) > 0 