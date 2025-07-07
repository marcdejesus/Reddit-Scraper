# Reddit SaaS Opportunity Finder

## Overview

**Reddit SaaS Opportunity Finder** is a command-line intelligence tool that identifies viable SaaS business opportunities by analyzing pain points expressed in Reddit discussions. This tool scrapes Reddit for relevant conversations, uses Natural Language Processing (NLP) to identify and categorize user-stated problems, and applies a machine learning model to score and rank potential SaaS opportunities.

This tool is designed for entrepreneurs, product managers, and indie hackers who want to build businesses that solve real-world problems.

## Features

-   **Advanced Data Collection**: Scrape posts and comments from multiple subreddits with fine-grained controls.
-   **Pain Point Detection**: Automatically identify mentions of problems, frustrations, and unmet needs in text.
-   **Opportunity Scoring**: Evaluate potential SaaS ideas based on market size, willingness to pay, and solution gaps.
-   **Trend Analysis**: Discover emerging trends and seasonal patterns in discussions.
-   **Data Export**: Export processed data to CSV, JSON, or text reports for further analysis.
-   **Customizable Configuration**: Tailor the tool to your needs with simple YAML configuration files.

## Installation

Follow these instructions to set up the Reddit SaaS Opportunity Finder on your local machine.

### Prerequisites

-   Python 3.9+
-   `pip` and `venv`

### Installation Steps

#### For macOS / Linux

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

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install the project in editable mode:**
    This makes the `reddit-finder` command available in your shell.
    ```bash
    pip install -e .
    ```

#### For Windows

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/reddit-saas-finder.git
    cd reddit-saas-finder
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    venv\\Scripts\\activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install the project in editable mode:**
    ```bash
    pip install -e .
    ```

## Configuration

Before running the tool, you need to configure your Reddit API credentials and other settings.

### 1. Reddit API Credentials

You will need a Reddit client ID and client secret. You can get these by creating a new "script" app on Reddit's [app preferences page](https://www.reddit.com/prefs/apps).

### 2. Configuration Files

The configuration is managed through YAML files located in the `reddit_saas_finder/config/` directory.

-   **`default.yaml`**: This file holds your Reddit API keys and general settings.
    ```yaml
    reddit:
      client_id: "YOUR_REDDIT_CLIENT_ID"
      client_secret: "YOUR_REDDIT_CLIENT_SECRET"
      user_agent: "RedditSaaSExpedition/1.0"
      rate_limit: 60
    
    data_collection:
      max_posts_per_subreddit: 1000
      min_score_threshold: 5
    ```

-   **`subreddits.yaml`**: Define lists of subreddits to scrape.
    ```yaml
    primary:
      - "SaaS"
      - "startup"
      - "entrepreneur"
    
    secondary:
      - "smallbusiness"
      - "growmybusiness"
    ```

You can view or open these files for editing using the `config` command.

## Example Workflow

Here is a typical workflow for using the tool from start to finish:

1.  **Initialize the Database**:
    Creates the necessary database file and tables.
    ```bash
    reddit-finder init-db
    ```

2.  **Scrape Data**:
    Collect posts and comments from a subreddit.
    ```bash
    reddit-finder scrape subreddit --name entrepreneur --limit 200
    ```

3.  **Process Pain Points**:
    Run the NLP pipeline to analyze the scraped text and identify pain points.
    ```bash
    reddit-finder process pain-points
    ```

4.  **Generate Opportunities**:
    Analyze the detected pain points to generate and score potential SaaS opportunities.
    ```bash
    reddit-finder opportunities generate
    ```

5.  **Export the Results**:
    Export the generated opportunities to a CSV file for further analysis.
    ```bash
    reddit-finder export --opportunities --format csv
    ```

## CLI Usage

Below are detailed examples for every command available in the tool.

### `init-db`
Initializes the SQLite database. Run this command first.

```bash
reddit-finder init-db
```

### `scrape`
Collects data from Reddit.

-   **Scrape a single subreddit:**
    ```bash
    reddit-finder scrape subreddit --name SaaS --limit 100 --time week
    ```
    *   `-n`, `--name`: The name of the subreddit.
    *   `-l`, `--limit`: The maximum number of posts to fetch.
    *   `-t`, `--time`: The time filter ('day', 'week', 'month', 'year', 'all').

### `process`
Processes the scraped text to find valuable insights.

-   **Detect pain points using the default NLP model:**
    ```bash
    reddit-finder process pain-points
    ```
-   **Use the advanced (slower but more accurate) model:**
    ```bash
    reddit-finder process pain-points --advanced
    ```

### `opportunities`
Generates, scores, and displays SaaS opportunities.

-   **Generate opportunities from detected pain points:**
    ```bash
    reddit-finder opportunities generate --min-points 5 --min-score 0.6
    ```
    *   `--min-points`: The minimum number of related pain points required to form an opportunity.
    *   `--min-score`: The minimum sentiment score for a pain point to be considered.

-   **Show a table of the top opportunities:**
    ```bash
    reddit-finder opportunities show
    ```

### `show`
Visualizes data directly in the terminal.

-   **Display top opportunities in a table:**
    ```bash
    reddit-finder show table --limit 15
    ```

-   **Show the distribution of opportunities by category:**
    ```bash
    reddit-finder show categories
    ```

### `export`
Exports processed data to various file formats.

-   **Export opportunities to a CSV file:**
    ```bash
    reddit-finder export --opportunities --format csv
    ```
-   **Export pain points to a JSON file with a custom name:**
    ```bash
    reddit-finder export --pain-points --format json --output my_pain_points.json
    ```

-   **Generate a text summary report:**
    ```bash
    reddit-finder export report --format txt
    ```

### `config`
Manages the application's configuration files.

-   **Show the contents of all configuration files:**
    ```bash
    reddit-finder config show
    ```
-   **Open the main configuration file in your default editor:**
    ```bash
    reddit-finder config edit
    ```

### `keywords`
Manages custom keywords for NLP processing.

-   **Add a new keyword:**
    ```bash
    reddit-finder keywords add "buggy software" --category "Technical Debt"
    ```
-   **List all keywords:**
    ```bash
    reddit-finder keywords list
    ```
-   **Remove a keyword:**
    ```bash
    reddit-finder keywords remove "buggy software"
    ```
-   **Export keywords to a YAML file:**
    ```bash
    reddit-finder keywords export --output custom_keywords.yaml
    ```

### `trends`
Analyzes trends in the data.

-   **Analyze opportunity trends over the last 90 days:**
    ```bash
    reddit-finder trends analyze --days 90
    ```
-   **Detect seasonal patterns in pain point discussions:**
    ```bash
    reddit-finder trends seasonal
    ```
-   **Predict the growth potential of a specific opportunity:**
    ```bash
    reddit-finder trends predict --id 42
    ```

### `validate`
Performs data quality and integrity checks.

-   **Run all data validation checks:**
    ```bash
    reddit-finder validate data
    ```
-   **Generate and display a data quality report:**
    ```bash
    reddit-finder validate report
    ```

### `optimize`
Tools for improving application performance.

-   **Clear the NLP cache:**
    ```bash
    reddit-finder optimize cache-clear
    ```
-   **Process data in smaller batches to conserve memory:**
    ```bash
    reddit-finder optimize batch-process --batch-size 50
    ```

### `schedule`
Manages background tasks for automated data collection.

-   **Start the background scheduler:**
    ```bash
    reddit-finder schedule start --interval 6
    ```
    *   `--interval`: The interval in hours between scraping runs.

-   **Stop the scheduler:**
    ```bash
    reddit-finder schedule stop
    ```
-   **Check the scheduler's status:**
    ```bash
    reddit-finder schedule status
    ```

## Troubleshooting

-   **AuthenticationError**: If you see this error, your Reddit API credentials in `config/default.yaml` are likely incorrect. Double-check your `client_id` and `client_secret`.
-   **No data scraped**: Ensure the subreddits you are targeting are active and spelled correctly. Try a broader time filter (e.g., `--time month`).
-   **Command not found**: Make sure you have activated the virtual environment (`source venv/bin/activate`) and installed the project in editable mode (`pip install -e .`).
-   **Database errors**: If you encounter a database error, you can reset it by deleting the `reddit_saas_finder/data/reddit_data.db` file and running `reddit-finder init-db` again.

---
Happy hunting! 