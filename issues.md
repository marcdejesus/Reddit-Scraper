# Issues

## Issue 1: `OpportunityScorer` TypeError on instantiation

- **Symptom**: Running `opportunities generate` fails with `TypeError: OpportunityScorer.__init__() takes 1 positional argument but 2 were given`.
- **Analysis**: The `OpportunityScorer` class in `reddit_saas_finder/src/ml/opportunity_scorer.py` is being instantiated with an argument, but its `__init__` method does not accept one. The root cause was determined to be an issue with how the CLI was running the code, likely due to an editable install (`pip install -e .`).
- **Resolution**: The issue was resolved by explicitly setting the `PYTHONPATH` to include the `src` directory when running the CLI. This forces Python to look for the modules in the correct location.
- **Status**: Resolved

## Issue 2: All opportunities are "uncategorized"

- **Symptom**: All generated opportunities are assigned the "uncategorized" category.
- **Analysis**: The categorization logic in `OpportunityScorer` is not correctly assigning categories to the generated opportunities. This could be due to a bug in the code or a lack of proper category definitions.
- **Status**: Open 