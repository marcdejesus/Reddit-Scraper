from setuptools import setup, find_packages

# Read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="reddit-saas-finder",
    version="1.0.0",
    author="Marc de Jesus",
    author_email="marcdejesusk@gmail.com",
    description="A CLI tool to find SaaS opportunities on Reddit.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marcdejesusk/Reddit-Scraper",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "reddit-finder=cli.main:app",
        ],
    },
    install_requires=[
        "typer[all]",
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
        "setuptools"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
) 