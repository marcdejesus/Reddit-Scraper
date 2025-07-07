"""Manages the generation and scoring of opportunities."""
from reddit_saas_finder.src.ml.opportunity_scorer import OpportunityScorer

def generate_and_score_opportunities():
    """
    Initializes the OpportunityScorer and runs the opportunity generation process.
    """
    scorer = OpportunityScorer()
    scorer.generate_opportunities() 