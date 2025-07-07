from setuptools import setup, find_packages

setup(
    name="reddit_saas_finder",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "reddit-finder=cli.main:app",
        ],
    },
    install_requires=[
        "typer",
        "praw",
        "spacy",
        "nltk",
        "transformers",
        "scikit-learn",
        "joblib",
        "pandas",
        "numpy",
        "rich",
        "PyYAML",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
        ]
    }
) 