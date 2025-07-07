"""Calculates various NLP-based scores."""
from transformers import pipeline, logging as transformers_logging
import warnings

# Suppress verbose logging from transformers
transformers_logging.set_verbosity_error()
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")


class SentimentScorer:
    """
    Scores text for sentiment and severity.
    """
    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis")

    def score_pain_point_severity(self, text: str):
        """
        Scores the severity of a pain point based on sentiment and keywords.
        Returns a score between 0.0 and 1.0.
        """
        sentiment = self.sentiment_analyzer(text)[0]
        base_score = sentiment['score'] if sentiment['label'] == 'NEGATIVE' else 0.1

        # Boost score for intensity words
        intensity_words = ['extremely', 'really', 'very', 'completely', 'totally', 'hate']
        intensity_boost = sum(0.1 for word in intensity_words if word in text.lower())

        # Boost score for urgency words
        urgency_words = ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'need']
        urgency_boost = sum(0.2 for word in urgency_words if word in text.lower())
        
        final_score = min(1.0, base_score + intensity_boost + urgency_boost)
        return final_score 