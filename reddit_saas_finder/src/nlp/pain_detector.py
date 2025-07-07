"""Detects pain points in text."""
import spacy
import re
from rich.console import Console
from transformers import pipeline, logging as transformers_logging
import warnings

# Suppress verbose logging from transformers
transformers_logging.set_verbosity_error()
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

console = Console()

class BasicPainDetector:
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
            r"I hate (that|when|how)", r"(really|so) frustrating", r"why (is|does|can't|won't)",
            r"(wish|need) there was", r"can't find (a|any) (way|tool|solution)", r"(struggling|having trouble) with",
            r"annoying", r"terrible", r"awful", r"sucks", r"problem", r"issue",
            r"difficulty", r"challenge", r"pain", r"waste time", r"takes forever",
            r"slow", r"inefficient", r"tedious", r"expensive", r"costly", r"missing feature",
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
                    pain_points.append({'content': sent.text, 'pattern': pattern})
                    break # Move to the next sentence after finding one match
        return pain_points

class AdvancedPainDetector(BasicPainDetector):
    """
    Detects pain points using a pre-trained transformer model for more accuracy.
    """
    def __init__(self):
        super().__init__()
        try:
            # Using a model fine-tuned for sentiment analysis on Twitter data, which is similar to Reddit's informal text.
            self.sentiment_classifier = pipeline(
                "sentiment-analysis", 
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
        except Exception as e:
            console.print(f"[bold red]Failed to load transformer model: {e}[/bold red]")
            console.print("[bold yellow]Falling back to basic pain point detection.[/bold yellow]")
            self.sentiment_classifier = None

    def extract_pain_points(self, text: str):
        """
        Overrides the basic method to use the advanced transformer-based approach.
        If the advanced model is unavailable, it falls back to the parent's method.
        """
        if not self.sentiment_classifier:
            return super().extract_pain_points(text)

        pain_points = []
        doc = self.nlp(text)
        
        for sent in doc.sents:
            # First, do a quick check with basic patterns to reduce the number of expensive model calls.
            if any(re.search(pattern, sent.text, re.IGNORECASE) for pattern in self.pain_point_patterns):
                result = self.sentiment_classifier(sent.text)[0]
                # We consider 'negative' sentiment as a strong indicator of a pain point.
                if result['label'] == 'negative' and result['score'] > 0.6: # Confidence threshold
                    pain_points.append({
                        'content': sent.text,
                        'confidence': result['score'],
                        'pattern': 'transformer-detected'
                    })
        return pain_points 