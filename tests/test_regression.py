import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
import os
import sqlite3
import tempfile
import shutil

from cli.main import app
from data.database import initialize_database, DB_PATH, get_db_connection

runner = CliRunner()

# --- Regression Test for Bug: `init-db` fails if db directory doesn't exist ---

def test_init_db_creates_directory():
    """
    Ensures the init-db command creates the database directory if it doesn't exist.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_db_path = os.path.join(tmpdir, "non_existent_dir", "test.db")
        
        with patch('data.database.DB_PATH', temp_db_path):
            result = runner.invoke(app, ["init-db"])
            assert result.exit_code == 0
            assert os.path.exists(temp_db_path)

# --- Regression Test for Bug: Scraper crashes on empty or invalid subreddit ---

@patch('data.reddit_client.praw.Reddit')
def test_scrape_invalid_subreddit(mock_reddit):
    """
    Tests that the scraper handles an invalid subreddit gracefully without crashing.
    """
    # Mock the PRAW client to raise an exception for an invalid subreddit.
    mock_reddit_instance = mock_reddit.return_value
    mock_reddit_instance.subreddit.side_effect = Exception("Subreddit not found or invalid.")

    result = runner.invoke(app, ["scrape", "subreddit", "--name", "invalidsubreddit"])
    assert result.exit_code == 0
    assert "An error occurred during scraping setup" in result.stdout

# --- Regression Test for Bug: API Rate Limit Error ---

@patch('data.reddit_client.praw.Reddit')
def test_scraper_handles_rate_limit(mock_reddit):
    """
    Ensures the scraper handles API rate limit errors gracefully.
    """
    # Configure the mock to raise a PRAW exception simulating a rate limit.
    from prawcore.exceptions import ResponseException
    mock_subreddit = mock_reddit.return_value.subreddit.return_value
    mock_subreddit.top.side_effect = ResponseException(MagicMock())

    result = runner.invoke(app, ["scrape", "subreddit", "--name", "any"])
    assert result.exit_code == 0
    assert "An error occurred while scraping" in result.stdout

# --- Regression Test for Bug: Corrupted Database File ---

def test_handles_corrupted_database():
    """
    Tests graceful handling of a corrupted or invalid SQLite file.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=True) as tmpfile:
        # The file is empty and thus a corrupted db
        
        with patch('data.database.DB_PATH', tmpfile.name):
            result = runner.invoke(app, ["init-db"], catch_exceptions=True)
            assert isinstance(result.exception, SystemExit)
            assert result.exit_code != 0 