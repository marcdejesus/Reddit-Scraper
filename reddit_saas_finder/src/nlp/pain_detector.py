"""Detects pain points in text."""
import spacy
import re
from rich.console import Console

console = Console()

class PainDetector:
    """
    Detects pain points in text using keyword matching and NLP.
    """
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            console.print("[bold yellow]spaCy model 'en_core_web_sm' not found. Downloading...[/bold yellow]")
            from spacy.cli import download
            download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
            
        # Using the patterns from the implementation plan
        self.pain_point_patterns = [
            r"I hate (that|when|how)",
            r"(really|so) frustrating",
            r"why (is|does|can't|won't)",
            r"(wish|need) there was",
            r"can't find (a|any) (way|tool|solution)",
            r"(struggling|having trouble) with",
            r"annoying",
            r"terrible",
            r"awful",
            r"sucks",
            r"problem",
            r"issue",
            r"difficulty",
            r"challenge",
            r"pain",
            r"waste time",
            r"takes forever",
            r"slow",
            r"inefficient",
            r"tedious",
            r"expensive",
            r"costly",
            r"missing feature",
        ]

    def extract_pain_points(self, text: str):
        """
        Extracts sentences that contain pain point indicators.
        """
        pain_points = []
        doc = self.nlp(text)
        
        for sent in doc.sents:
            for pattern in self.pain_point_patterns:
                if re.search(pattern, sent.text, re.IGNORECASE):
                    pain_points.append({
                        'content': sent.text,
                        'pattern': pattern,
                    })
                    # Move to the next sentence after finding one match
                    break
        return pain_points 