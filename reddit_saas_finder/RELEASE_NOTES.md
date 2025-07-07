# Release Notes

## Version 1.0.0 - Initial Release (Current)

**Release Date:** July 7, 2025

This is the first official release of the **Reddit SaaS Opportunity Finder**. This version provides a robust set of tools for entrepreneurs, product managers, and indie hackers to discover and validate SaaS ideas by analyzing discussions on Reddit.

### ✨ Features

-   **Command-Line Interface**: A comprehensive CLI for scraping Reddit, processing data, and generating insights.
-   **Advanced NLP Processing**: Leverages transformer-based models for sophisticated pain point detection and sentiment analysis.
-   **Rich Terminal Visualizations**: Uses the Rich library to display data in beautifully formatted tables and charts directly in the terminal.
-   **Flexible Data Export**: Export opportunities, pain points, and reports to multiple formats, including CSV, JSON, and plain text.
-   **Automated Scheduling**: A built-in scheduler allows you to automate data scraping and processing tasks to run at regular intervals.
-   **Performance Optimization Tools**: Includes utilities for profiling CLI commands and optimizing the database.

### ⚠️ Known Limitations

-   **Database Performance**: While indexing is implemented, performance may degrade on extremely large datasets (over 1 million records). Further optimization is planned.
-   **Configuration File Path**: The tool currently looks for configuration files (`default.yaml`, `subreddits.yaml`, etc.) in the directory from which it is executed. In a future release, we will add support for a global user-level configuration directory (e.g., `~/.config/reddit-saas-finder/`).
-   **NLP Model Accuracy**: The NLP models are powerful but have not been fine-tuned on Reddit-specific language. This may lead to occasional inaccuracies in pain point detection and sentiment analysis.

### 🚀 Upgrade Instructions

When a new version is released, you can upgrade your installation by running the following command:

```bash
pip install --upgrade reddit-saas-finder
```

To ensure you have the latest dependencies and features, it is recommended to run this command periodically. 