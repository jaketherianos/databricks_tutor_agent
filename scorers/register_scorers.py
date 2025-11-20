"""
Register MLflow 3 Production Scorers

Registers the 3 scorers defined in scorers.py for production monitoring.
https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/production-monitoring

⚠️  IMPORTANT: Production scorer registration requires Databricks or a database backend.
    Local file-based tracking (file://) is NOT supported.

Usage:
  - In Databricks: Run this script in a notebook or job
  - Locally: Set tracking URI to sqlite:///mlflow.db first
"""

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import mlflow
import os

experiment_id = os.environ.get("MLFLOW_EXPERIMENT_ID")
databricks_host = os.environ.get("DATABRICKS_HOST")
mlflow_tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")
print(f"Experiment ID: {experiment_id}")
print(f"Tracking URI: {mlflow_tracking_uri}")

from mlflow.genai.scorers import ScorerSamplingConfig
from scorers import relevance_scorer, completeness_scorer, difficulty_scorer
print("Registering production scorers...\n")

from mlflow.genai.scorers import get_scorer

# 1. Relevance Scorer (LLM, 100% sample)
try:
    relevance = relevance_scorer.register(name="tutor_relevance")
    relevance = relevance.start(sampling_config=ScorerSamplingConfig(sample_rate=1.0))
    print("✅ Relevance scorer registered (100% sample)")
except ValueError:
    relevance = get_scorer(name="tutor_relevance")
    relevance = relevance.update(sampling_config=ScorerSamplingConfig(sample_rate=1.0))
    print("✅ Relevance scorer updated (100% sample)")

# 2. Completeness Scorer (Code-based, 100% sample)
try:
    completeness = completeness_scorer.register(name="tutor_completeness")
    completeness = completeness.start(sampling_config=ScorerSamplingConfig(sample_rate=1.0))
    print("✅ Completeness scorer registered (100% sample)")
except ValueError:
    completeness = get_scorer(name="tutor_completeness")
    completeness = completeness.update(sampling_config=ScorerSamplingConfig(sample_rate=1.0))
    print("✅ Completeness scorer updated (100% sample)")

# 3. Difficulty Alignment Scorer (LLM, 100% sample)
try:
    difficulty = difficulty_scorer.register(name="tutor_difficulty")
    difficulty = difficulty.start(sampling_config=ScorerSamplingConfig(sample_rate=1.0))
    print("✅ Difficulty scorer registered (100% sample)")
except ValueError:
    difficulty = get_scorer(name="tutor_difficulty")
    difficulty = difficulty.update(sampling_config=ScorerSamplingConfig(sample_rate=1.0))
    print("✅ Difficulty scorer updated (100% sample)")

print("\n🚀 All scorers active and monitoring production traces!")
