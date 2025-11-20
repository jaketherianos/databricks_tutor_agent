# MLflow 3 Scorers for Production Monitoring

This guide demonstrates three types of MLflow scorers for evaluating the Small Tutor Agent in production.

## 📋 Overview

| Scorer Type | Speed | Cost | Use Case |
|------------|-------|------|----------|
| **Code-Based** | ⚡ Fast | 💰 Free | Real-time monitoring, CI/CD gates |
| **Built-in LLM Judge** | 🐌 Slow | 💰💰 Paid | Relevance checks, semantic quality |
| **Custom LLM Judge** | 🐌 Slow | 💰💰 Paid | Domain-specific validation |

---

## 🎯 The Three Scorers

### 1. Built-in Judge: Relevance Scorer

**What it does:** Uses MLflow's pre-built relevance metric to check if the output actually answers the input topic.

**Why it's valuable:**
- ✅ Catches hallucinations where the model goes off-topic
- ✅ Detects model drift over time
- ✅ Battle-tested by MLflow team, no custom code needed

**Example:**
```python
from scorers import relevance_scorer

# Use in evaluation
results = mlflow.evaluate(
    model=your_model,
    data=eval_data,
    extra_metrics=[relevance_scorer]
)
```

**Production Use Case:**
> *"We noticed our agent started talking about Spark when users asked about Unity Catalog. The relevance scorer dropped from 4.8 to 3.2, alerting us to investigate."*

---

### 2. Custom LLM Judge: Difficulty Alignment Scorer

**What it does:** Evaluates whether explanations match their intended difficulty level (beginner/intermediate/expert).

**Why it's valuable:**
- ✅ Ensures consistent quality across all difficulty levels
- ✅ Catches when the model generates overly complex beginner explanations
- ✅ Validates that expert explanations include advanced concepts

**How it works:**
```python
from scorers import difficulty_alignment_scorer

# The scorer checks:
# - Beginner: Simple language, no jargon, analogies
# - Intermediate: Technical terms with explanations
# - Expert: Advanced terminology, nuances, trade-offs
```

**Production Use Case:**
> *"Our beginner explanations started using terms like 'MVCC' and 'ACID transactions' without explanation. The difficulty alignment score dropped to 2.1/5, triggering a review of our system prompt."*

---

### 3. Code-Based Judge: Completeness & Readability Scorer

**What it does:** Fast, deterministic checks for basic quality metrics.

**Metrics tracked:**
- ✅ **Completeness**: All 3 levels present and non-empty
- ✅ **Length**: 50-300 words per explanation (optimal range)
- ✅ **Readability**: Multiple sentences, paragraph structure
- ✅ **Progression**: Expert explanations more detailed than beginner

**Why it's valuable:**
- ⚡ Runs in milliseconds, no API calls
- 💰 Zero cost
- 🚦 Perfect for real-time quality gates
- 🔍 Catches truncation, empty responses, formatting issues

**Example:**
```python
from scorers import evaluate_tutor_response

response = run_tutor_agent("Delta Lake")
scores = evaluate_tutor_response("Delta Lake", response)

print(f"Completeness: {scores['completeness_score']}")
print(f"Overall Quality: {scores['overall_quality']}")

# Use as quality gate
if scores['overall_quality'] < 0.7:
    alert_team()
```

**Production Use Case:**
> *"We deployed a new model that sometimes returned truncated responses. The completeness scorer immediately caught this in our staging environment before it hit production."*

---

## 🚀 Quick Start

### Run the Demo

```bash
# Install dependencies
pip install -r requirements.txt

# Run quick evaluation (code-based only, no API keys needed)
python evaluate_tutor.py
```

### Use Individual Scorers

```python
from scorers import (
    relevance_scorer,           # Built-in LLM judge
    difficulty_alignment_scorer, # Custom LLM judge  
    completeness_metric         # Code-based
)

# Quick code-based evaluation
from scorers import evaluate_tutor_response
scores = evaluate_tutor_response(topic, response)
```

---

## 💡 Production Strategies

### Strategy 1: Tiered Evaluation

**Use code-based as a pre-filter:**

```python
# Step 1: Fast code-based check (runs on every request)
scores = evaluate_tutor_response(topic, response)

# Step 2: Only run expensive LLM judges if basic quality passes
if scores['overall_quality'] >= 0.7:
    # Sample 10% for deeper evaluation
    if random.random() < 0.1:
        run_llm_judges(topic, response)
```

**Benefits:**
- 💰 Save 90% on evaluation costs
- ⚡ Real-time feedback on basic quality
- 🎯 Deep analysis on subset of traffic

---

### Strategy 2: CI/CD Quality Gates

**Block deployments with failing scores:**

```python
# In your deployment pipeline
def validate_model_quality():
    eval_results = mlflow.evaluate(
        model=new_model,
        data=golden_test_set,
        extra_metrics=[completeness_metric]
    )
    
    if eval_results.metrics['overall_quality'] < 0.8:
        raise Exception("Model failed quality gate!")
    
    return True
```

---

### Strategy 3: Continuous Monitoring

**Track metrics over time:**

```python
# Log all scores to MLflow
with mlflow.start_run():
    scores = evaluate_tutor_response(topic, response)
    
    for metric_name, value in scores.items():
        mlflow.log_metric(metric_name, value)
    
    # Alert if quality degrades
    if scores['overall_quality'] < historical_avg * 0.9:
        send_alert("Model quality degraded!")
```

**Dashboard Example:**
```
Week 1: Avg Quality = 0.85 ✅
Week 2: Avg Quality = 0.84 ✅
Week 3: Avg Quality = 0.72 ⚠️  <- Alert triggered
Week 4: Investigate & fix
```

---

### Strategy 4: A/B Testing

**Compare model versions systematically:**

```python
# Test current vs new model
topics = load_test_topics()

for topic in topics:
    response_a = current_model(topic)
    response_b = new_model(topic)
    
    scores_a = evaluate_tutor_response(topic, response_a)
    scores_b = evaluate_tutor_response(topic, response_b)
    
    log_comparison(scores_a, scores_b)

# Automatically promote if consistently better
if avg(scores_b) > avg(scores_a) * 1.05:
    promote_to_production(new_model)
```

---

## 📊 Interpreting Scores

### Completeness Score (0-1)
- **1.0**: All 3 levels present ✅
- **0.0**: Missing levels ❌

### Length Score (0-1)
- **1.0**: 50-300 words (optimal)
- **0.8**: 300-500 words (acceptable)
- **0.5**: <30 words (too short)

### Readability Score (0-1)
- **1.0**: Multiple sentences, good structure
- **0.5**: Poor structure or too simple

### Progression Score (0-1)
- **1.0**: Clear complexity progression
- **0.5**: Some progression
- **0.0**: No progression (all same length/complexity)

### Overall Quality (0-1)
Weighted combination:
- 30% Completeness
- 30% Length
- 20% Readability  
- 20% Progression

**Quality Gates:**
- **≥ 0.8**: Excellent ⭐⭐⭐
- **0.7-0.8**: Good ✅
- **0.5-0.7**: Acceptable ⚠️
- **< 0.5**: Poor ❌

---

## 🛠️ Customization

### Add Your Own Code-Based Metrics

```python
def custom_scorer(inputs, outputs, context=None):
    scores = {}
    
    # Example: Check for specific keywords
    beginner_text = outputs['beginner'].lower()
    has_analogy = any(word in beginner_text 
                     for word in ['like', 'similar to', 'imagine'])
    scores['has_analogy'] = 1.0 if has_analogy else 0.0
    
    return scores
```

### Customize LLM Judge Prompts

```python
from mlflow.metrics.genai import make_genai_metric

my_judge = make_genai_metric(
    name="custom_metric",
    definition="Your definition here",
    grading_prompt="Your custom prompt with {inputs} and {outputs}",
    examples=[...],
    model="openai:/gpt-4"
)
```

---

## 🎓 Best Practices

### 1. Start Simple
- ✅ Begin with code-based metrics
- ✅ Add LLM judges only when needed
- ✅ Monitor costs carefully

### 2. Establish Baselines
- ✅ Run scorers on golden test set
- ✅ Document expected score ranges
- ✅ Set alerts for deviations

### 3. Sample Strategically
- ✅ 100% code-based (free)
- ✅ 10% LLM judges (expensive)
- ✅ 100% on failures for debugging

### 4. Version Everything
- ✅ Track scorer versions
- ✅ Log evaluation configs
- ✅ Compare scores over time

### 5. Close the Loop
- ✅ Log feedback to improve scorers
- ✅ Update thresholds based on production data
- ✅ Continuously refine quality definitions

---

## 🔗 Integration Examples

### With Streamlit App

```python
# In app.py
from scorers import evaluate_tutor_response

# After generating response
scores = evaluate_tutor_response(topic, response)

# Show quality indicator in UI
if scores['overall_quality'] >= 0.8:
    st.success(f"High quality response (score: {scores['overall_quality']:.2f})")
```

### With Databricks Jobs

```python
# In scheduled job
def daily_quality_check():
    # Sample last 100 production requests
    requests = load_production_logs(limit=100)
    
    quality_scores = []
    for req in requests:
        scores = evaluate_tutor_response(req.topic, req.response)
        quality_scores.append(scores['overall_quality'])
    
    avg_quality = mean(quality_scores)
    
    # Log to MLflow for trending
    mlflow.log_metric("daily_avg_quality", avg_quality)
    
    if avg_quality < 0.75:
        send_slack_alert(f"Quality dropped to {avg_quality:.2f}")
```

---

## 📚 Additional Resources

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [MLflow GenAI Metrics Guide](https://mlflow.org/docs/latest/llms/llm-evaluate/index.html)
- [Building Custom Metrics](https://mlflow.org/docs/latest/python_api/mlflow.metrics.html)

---

## 🤝 Contributing

Have ideas for new scorers? Found a bug? 

1. Test your scorer on diverse inputs
2. Document the production value
3. Include examples and thresholds
4. Submit with test cases

---

**Happy Monitoring! 📊✨**

