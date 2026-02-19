# Evaluation Guide: Using Azure AI Foundry

This guide shows you how to use Azure AI Foundry evaluations to ensure GPT-5.1 meets your quality standards before production deployment.

## Why Evaluate?

Migration without evaluation is risky:
- You might miss quality regressions
- Edge cases could slip through
- Stakeholders have no evidence of success

With proper evaluation:
- Quantifiable quality metrics
- Side-by-side model comparison
- Confidence in deployment decisions
- Evidence for stakeholder sign-off

---

## Evaluation Methods

### 1. Azure AI Evaluation SDK (Local)

Best for: Development, CI/CD pipelines, quick iteration

```bash
pip install azure-ai-evaluation
```

### 2. Foundry Portal (UI)

Best for: Visual comparison, stakeholder demos, one-time runs

Access at: https://ai.azure.com

### 3. Cloud Evaluation API

Best for: Large-scale testing, production monitoring

---

## Setting Up Local Evaluation

### Step 1: Install Dependencies

```bash
pip install azure-ai-evaluation openai azure-identity
```

### Step 2: Configure the Judge Model

Evaluations use an LLM (the "judge") to score responses. GPT-4o is recommended:

```python
from azure.ai.evaluation import AzureOpenAIModelConfiguration

judge_config = AzureOpenAIModelConfiguration(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_deployment="gpt-4o",  # Judge model
    api_version="2024-10-21"
)
```

### Step 3: Initialize Evaluators

```python
from azure.ai.evaluation import (
    CoherenceEvaluator,
    FluencyEvaluator,
    RelevanceEvaluator,
    GroundednessEvaluator,
    SimilarityEvaluator
)

evaluators = {
    "coherence": CoherenceEvaluator(model_config=judge_config),
    "fluency": FluencyEvaluator(model_config=judge_config),
    "relevance": RelevanceEvaluator(model_config=judge_config),
    "groundedness": GroundednessEvaluator(model_config=judge_config),
    "similarity": SimilarityEvaluator(model_config=judge_config)
}
```

---

## Understanding the Metrics

### Coherence (1-5)
**What it measures**: Logical flow, clear transitions, well-organized response

**When it matters**: Any response longer than a sentence

**Example**:
- Score 5: Response flows naturally, ideas connect logically
- Score 3: Some disjointed parts, but overall understandable
- Score 1: Confusing, contradictory, hard to follow

### Fluency (1-5)
**What it measures**: Grammar, spelling, natural language

**When it matters**: Customer-facing text, professional communications

**Example**:
- Score 5: Perfect grammar, natural phrasing
- Score 3: Minor errors, slightly awkward phrasing
- Score 1: Major errors, broken sentences

### Relevance (1-5)
**What it measures**: How well the response addresses the query

**When it matters**: All responses — this is often the most important metric

**Example**:
- Score 5: Directly and completely addresses the question
- Score 3: Partially addresses, missing key points
- Score 1: Off-topic or irrelevant

### Groundedness (1-5)
**What it measures**: Factual alignment with provided context

**When it matters**: RAG applications, customer data lookups

**Example**:
- Score 5: All claims supported by context
- Score 3: Some unsupported claims
- Score 1: Significant hallucination

### Similarity (1-5)
**What it measures**: Semantic similarity to ground truth response

**When it matters**: Regression testing against known-good responses

**Example**:
- Score 5: Nearly identical meaning to ground truth
- Score 3: Same general idea, different details
- Score 1: Completely different response

---

## Running Evaluations

### Single Response Evaluation

```python
# Evaluate one response
result = evaluators["coherence"](
    query="What's my bill amount?",
    response="Your current bill is 250 QAR, due on March 1st."
)
print(f"Coherence: {result['score']}")
```

### Batch Evaluation with Dataset

```python
from azure.ai.evaluation import evaluate

# Run evaluation on entire dataset
results = evaluate(
    data="golden_dataset.jsonl",
    evaluators=evaluators,
    output_path="./evaluation_results.json"
)

# Print summary
print(f"Average Coherence: {results['metrics']['coherence']['mean']}")
print(f"Average Relevance: {results['metrics']['relevance']['mean']}")
```

---

## Comparing GPT-4o vs GPT-5.1

### Step 1: Generate Responses from Both Models

```python
def generate_responses(dataset_path, model_name, client):
    """Generate responses for all test cases."""
    results = []
    with open(dataset_path) as f:
        for line in f:
            test_case = json.loads(line)
            
            # Call the appropriate model
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "developer", "content": "You are a helpful assistant."},
                    {"role": "user", "content": test_case["query"]}
                ],
                max_completion_tokens=500
            )
            
            results.append({
                "test_id": test_case["test_id"],
                "query": test_case["query"],
                "response": response.choices[0].message.content,
                "ground_truth": test_case["ground_truth"]
            })
    
    return results

# Generate from both models
gpt4o_responses = generate_responses("golden_dataset.jsonl", "gpt-4o", client_4o)
gpt51_responses = generate_responses("golden_dataset.jsonl", "gpt-5.1", client_51)
```

### Step 2: Evaluate Both Sets

```python
def evaluate_responses(responses, evaluators):
    """Evaluate all responses and return scores."""
    scores = {metric: [] for metric in evaluators}
    
    for r in responses:
        for metric, evaluator in evaluators.items():
            if metric == "similarity":
                result = evaluator(
                    query=r["query"],
                    response=r["response"],
                    ground_truth=r["ground_truth"]
                )
            else:
                result = evaluator(
                    query=r["query"],
                    response=r["response"]
                )
            scores[metric].append(result["score"])
    
    # Calculate averages
    return {m: sum(s)/len(s) for m, s in scores.items()}

gpt4o_scores = evaluate_responses(gpt4o_responses, evaluators)
gpt51_scores = evaluate_responses(gpt51_responses, evaluators)
```

### Step 3: Compare and Report

```python
def compare_scores(baseline, candidate, threshold=0.1):
    """Compare scores and flag regressions."""
    print("\n" + "="*60)
    print("EVALUATION COMPARISON: GPT-4o vs GPT-5.1")
    print("="*60)
    
    regressions = []
    for metric in baseline:
        diff = candidate[metric] - baseline[metric]
        diff_pct = diff / baseline[metric] * 100 if baseline[metric] > 0 else 0
        
        status = "✅" if diff >= -threshold else "⚠️ REGRESSION"
        if diff < -threshold:
            regressions.append(metric)
        
        print(f"{metric:15} | GPT-4o: {baseline[metric]:.2f} | "
              f"GPT-5.1: {candidate[metric]:.2f} | {diff_pct:+.1f}% {status}")
    
    print("="*60)
    if regressions:
        print(f"⚠️  Regressions detected in: {', '.join(regressions)}")
    else:
        print("✅ No significant regressions detected!")
    
    return regressions

regressions = compare_scores(gpt4o_scores, gpt51_scores)
```

---

## Using Foundry Portal

### Step 1: Navigate to Evaluations

1. Go to https://ai.azure.com
2. Select your project
3. Click "Evaluation" in the left menu

### Step 2: Create New Evaluation

1. Click "Create new evaluation"
2. Upload your dataset (JSONL or CSV)
3. Select evaluators:
   - AI Quality (Coherence, Fluency, Relevance)
   - Safety (if needed)
   - Custom (if you have custom evaluators)

### Step 3: Map Data Columns

Tell Foundry which columns in your dataset correspond to:
- **Query**: The input/question
- **Response**: The model's output
- **Context**: Additional context (optional)
- **Ground Truth**: Expected output (for similarity)

### Step 4: Run and Review

- Click "Run evaluation"
- Wait for completion (may take several minutes)
- Review results in the dashboard
- Export for further analysis

---

## Setting Quality Gates

### Define Acceptance Criteria

```python
ACCEPTANCE_CRITERIA = {
    "coherence": {"min": 4.0, "regression_threshold": 0.1},
    "fluency": {"min": 4.0, "regression_threshold": 0.1},
    "relevance": {"min": 4.0, "regression_threshold": 0.1},
    "groundedness": {"min": 3.5, "regression_threshold": 0.1},
    "similarity": {"min": 3.5, "regression_threshold": 0.15}
}

def check_quality_gates(scores, baseline_scores, criteria):
    """Check if scores meet acceptance criteria."""
    passed = True
    
    for metric, thresholds in criteria.items():
        score = scores.get(metric, 0)
        baseline = baseline_scores.get(metric, 0)
        
        # Check minimum score
        if score < thresholds["min"]:
            print(f"❌ {metric}: {score:.2f} below minimum {thresholds['min']}")
            passed = False
        
        # Check regression
        if baseline > 0:
            regression = (baseline - score) / baseline
            if regression > thresholds["regression_threshold"]:
                print(f"❌ {metric}: {regression:.1%} regression (threshold: {thresholds['regression_threshold']:.1%})")
                passed = False
    
    return passed

# Use in CI/CD
if not check_quality_gates(gpt51_scores, gpt4o_scores, ACCEPTANCE_CRITERIA):
    raise Exception("Quality gates failed - migration not approved")
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Model Evaluation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install azure-ai-evaluation openai
      
      - name: Run evaluation
        env:
          AZURE_OPENAI_ENDPOINT: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
          AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
        run: |
          python scripts/run_evaluation.py --dataset datasets/golden_dataset.jsonl
      
      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: evaluation-results
          path: evaluation_results.json
```

---

## Continuous Production Monitoring

### Sample Production Traffic

```python
import random

def handle_request(user_input):
    response = get_model_response(user_input)
    
    # Sample 5% of traffic for evaluation
    if random.random() < 0.05:
        evaluate_async(user_input, response)
    
    return response

async def evaluate_async(query, response):
    """Run evaluation in background."""
    scores = {}
    for metric, evaluator in evaluators.items():
        result = evaluator(query=query, response=response)
        scores[metric] = result["score"]
    
    # Log to monitoring system
    log_to_azure_monitor(scores)
    
    # Alert if below threshold
    if any(s < 3.5 for s in scores.values()):
        send_alert(f"Low quality response detected: {scores}")
```

### Set Up Alerts

In Azure Monitor, create alerts for:
- Quality score drops below threshold
- Spike in low-quality responses
- Evaluation failures

---

## Troubleshooting

### "Evaluation takes too long"

- Reduce dataset size for initial testing
- Use parallel evaluation
- Consider cloud evaluation for large datasets

### "Scores seem inconsistent"

- LLM judges have some variance
- Run multiple times and average
- Use larger datasets for reliable means

### "Groundedness score is low"

- Ensure context is passed to evaluator
- Check that responses actually use the context
- May need to improve RAG retrieval

### "Similarity score is low but response is good"

- Ground truth may be too specific
- Consider if ground truth needs updating
- Low similarity doesn't always mean bad quality

---

## Best Practices

1. **Establish baseline first** — Always evaluate GPT-4o before testing GPT-5.1

2. **Use consistent datasets** — Same test cases for both models

3. **Include edge cases** — Don't just test happy paths

4. **Review failures manually** — Automated scores miss nuance

5. **Get human validation** — Show results to domain experts

6. **Document decisions** — Record why you accepted certain regressions

7. **Monitor continuously** — Evaluation doesn't stop after migration

---

*Need help setting up evaluations? Your Microsoft Customer Success team can assist!*
