# Reddit SaaS Finder

## Project Overview
This project is a command-line intelligence tool that identifies viable SaaS business opportunities by analyzing pain points expressed in Reddit discussions. This CLI tool scrapes Reddit data, identifies pain points using NLP, and scores SaaS opportunities.

## Technology Stack
- **Language**: Python 3.9+
- **CLI Framework**: Typer
- **Reddit API**: PRAW (Python Reddit API Wrapper)
- **Database**: SQLite 3.x (via Python's built-in `sqlite3` module)
- **NLP Libraries**: spaCy, NLTK, Transformers (Hugging Face), scikit-learn
- **ML Libraries**: scikit-learn, joblib
- **Data Processing**: pandas, numpy
- **Terminal UI**: Rich
- **Configuration**: PyYAML

## Installation Instructions

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/reddit-saas-finder.git
    cd reddit-saas-finder
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    On Windows, use: `venv\Scripts\activate`

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install the project in editable mode:**
    ```bash
    pip install -e .
    ```

## Basic Usage

Here are some examples of how to use the CLI:

- **Scrape a specific subreddit:**
  ```bash
  reddit-finder scrape --subreddit entrepreneur --limit 200 --time week
  ```

- **Scrape multiple subreddits from a config file:**
  ```bash
  reddit-finder scrape --config subreddits.yaml --time month
  ```

- **Show the current scraping status:**
  ```bash
  reddit-finder status
  ``` 