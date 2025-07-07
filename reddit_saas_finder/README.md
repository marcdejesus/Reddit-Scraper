# Reddit SaaS Finder

This project is a command-line intelligence tool that identifies viable SaaS business opportunities by analyzing pain points expressed in Reddit discussions.

### Core Technologies
- **Python 3.9+**
- **Typer** for the CLI
- **PRAW** for Reddit API access
- **SQLite3** for the database (via Python's built-in `sqlite3` module)
- **spaCy**, **NLTK**, and **Transformers** for NLP
- **pandas** and **numpy** for data handling
- **Rich** for terminal UI

## Development

To install the project for development:

```bash
pip install -e .[dev]
```

To run the tool:

```bash
reddit-finder --help
``` 