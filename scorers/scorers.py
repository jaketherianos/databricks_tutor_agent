"""
MLflow 3 Production Scorers for Small Tutor Agent

Defines 3 scorers for production monitoring:
1. RelevanceToQuery - Built-in LLM judge
2. Completeness - Code-based deterministic scorer
3. Difficulty Alignment - Custom LLM judge
"""

from mlflow.genai.scorers import RelevanceToQuery, scorer


# ============================================================================
# 1. BUILT-IN RELEVANCE SCORER
# ============================================================================

relevance_scorer = RelevanceToQuery(
    name="tutor_relevance",
    model="databricks:/databricks-gpt-5-mini"
)


# ============================================================================
# 2. CODE-BASED COMPLETENESS SCORER
# ============================================================================

@scorer(aggregations=["mean", "min", "max"])
def completeness_scorer(outputs):
    """
    Fast, deterministic scorer that checks tutor response quality.
    Returns overall quality score 0-1.
    """
    required = ["beginner", "intermediate", "expert"]
    
    # Check all levels present
    if not all(level in outputs and outputs[level] for level in required):
        return 0.0
    
    # Check length (50-300 words is optimal)
    score = 0.0
    for level in required:
        words = len(str(outputs[level]).split())
        if 50 <= words <= 300:
            score += 1.0
        elif words < 50:
            score += 0.3
        else:
            score += 0.7
    
    return score / 3.0


# ============================================================================
# 3. CUSTOM DIFFICULTY ALIGNMENT SCORER
# ============================================================================

@scorer
def difficulty_scorer(inputs, outputs):
    """
    Custom LLM judge that validates explanations match difficulty levels.
    Checks beginner/intermediate/expert appropriateness.
    """
    from mlflow.genai.judges import custom_prompt_judge
    from mlflow.entities.assessment import DEFAULT_FEEDBACK_NAME
    
    prompt = """
    Evaluate if explanations match their difficulty levels:
    
    Topic: {{topic}}
    Beginner: {{beginner}}
    Intermediate: {{intermediate}}
    Expert: {{expert}}
    
    Beginner should use simple language, no jargon.
    Intermediate should balance accessibility with technical terms.
    Expert should use advanced terminology and discuss nuances.
    
    Choose one:
    [[excellent]]: All three levels perfectly match
    [[good]]: Minor misalignments but acceptable
    [[poor]]: Significant misalignment
    """
    
    judge = custom_prompt_judge(
        name="difficulty_alignment",
        prompt_template=prompt,
        numeric_values={"excellent": 1.0, "good": 0.7, "poor": 0.3},
        model="databricks:/databricks-gpt-5-mini"
    )
    
    result = judge(
        topic=inputs.get("topic", ""),
        beginner=outputs.get("beginner", ""),
        intermediate=outputs.get("intermediate", ""),
        expert=outputs.get("expert", "")
    )
    
    if hasattr(result, "name"):
        result.name = DEFAULT_FEEDBACK_NAME
    
    return result
