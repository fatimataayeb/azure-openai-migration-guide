# Migration Guide: GPT-4o to GPT-5.1

This guide walks you through migrating your Azure OpenAI applications from GPT-4o to GPT-5.1. The process is straightforward, and we'll help you every step of the way.

## Overview

GPT-5.1 brings significant improvements over GPT-4o:
- Better reasoning capabilities with adjustable depth
- Improved instruction following
- Lower input costs (50% reduction)
- Reduced hallucination rates

The migration requires some code changes, but they're well-documented and easy to implement.

---

## Phase 1: Discovery (Week 1)

### Step 1.1: Inventory Your Deployments

First, understand what you have deployed:

```bash
# List all Azure OpenAI deployments
az cognitiveservices account deployment list \
  --name <your-resource-name> \
  --resource-group <your-rg> \
  --output table
```

Document:
- Deployment names
- Deployment types (Standard PayGo vs PTU)
- Which applications use each deployment
- Current API versions in use

### Step 1.2: Understand Your Timeline

| Deployment Type | Auto-Upgrade Date | Retirement Date | Action Required |
|-----------------|-------------------|-----------------|-----------------|
| Standard (Regional) | March 9, 2026 | March 31, 2026 | Code updates needed |
| Global Standard | March 9, 2026 | March 31, 2026 | Code updates needed |
| PTU (Provisioned) | None (manual) | October 1, 2026 | Manual migration |

### Step 1.3: Audit Your Codebase

Search for parameters that need to change:

```bash
# Find temperature usage
grep -r "temperature" --include="*.py" --include="*.js" --include="*.ts" .

# Find max_tokens usage
grep -r "max_tokens" --include="*.py" --include="*.js" --include="*.ts" .

# Find system role usage
grep -r '"system"' --include="*.py" --include="*.js" --include="*.ts" .
grep -r "'system'" --include="*.py" --include="*.js" --include="*.ts" .
```

Or use our audit script:
```bash
python scripts/audit_codebase.py --path /your/code/path
```

---

## Phase 2: Code Updates (Week 2)

### Step 2.1: Update API Version

```python
# Before
client = AzureOpenAI(
    api_version="2024-10-21",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"]
)

# After
client = AzureOpenAI(
    api_version="2025-06-01",  # Updated
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"]
)
```

### Step 2.2: Update Model Name

```python
# Before
model="gpt-4o"

# After
model="gpt-5.1"
```

### Step 2.3: Remove Unsupported Parameters

These parameters are no longer supported and will cause errors:

```python
# Before (GPT-4o)
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    temperature=0.7,          # ❌ Remove
    top_p=0.95,               # ❌ Remove
    frequency_penalty=0.3,    # ❌ Remove
    presence_penalty=0.1,     # ❌ Remove
    max_tokens=500            # ❌ Change parameter name
)

# After (GPT-5.1)
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages,
    max_completion_tokens=500,  # ✅ Renamed parameter
    reasoning_effort="low"       # ✅ New parameter (optional)
)
```

### Step 2.4: Update Message Roles

```python
# Before
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": user_input}
]

# After
messages = [
    {"role": "developer", "content": "You are a helpful assistant."},
    {"role": "user", "content": user_input}
]
```

> **Note**: `system` still works but is deprecated. Using `developer` is recommended for clarity and future compatibility.

### Step 2.5: Add reasoning_effort Parameter

This new parameter controls how much "thinking" the model does:

| Value | Use Case | Cost Impact |
|-------|----------|-------------|
| `"none"` | Simple tasks: classification, extraction, quick lookups | Lowest |
| `"low"` | Standard responses: most customer interactions | Low |
| `"medium"` | Complex analysis: detailed reports, complaints | Medium |
| `"high"` | Critical decisions: requires deep analysis | Highest |

```python
# Simple classification - use "none"
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages,
    max_completion_tokens=100,
    reasoning_effort="none"
)

# Customer service response - use "low"
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages,
    max_completion_tokens=500,
    reasoning_effort="low"
)

# Complex complaint analysis - use "medium"
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages,
    max_completion_tokens=1000,
    reasoning_effort="medium"
)
```

> ⚠️ **Important**: `reasoning_effort` defaults to `"none"`. If your application relied on GPT-4o's default behavior, you may need to explicitly set `"low"` or higher to maintain similar response quality.

---

## Phase 3: Testing (Weeks 2-4)

### Step 3.1: Create Golden Dataset

Build a test dataset with at least 50 examples. See [Building Golden Datasets](golden-datasets.md) for detailed guidance.

Quick template:
```json
{"query": "Customer question here", "context": "{...}", "expected_output": "Expected response", "category": "billing"}
{"query": "Another question", "context": "{...}", "expected_output": "Expected response", "category": "technical"}
```

### Step 3.2: Set Up Evaluation Pipeline

```python
from azure.ai.evaluation import (
    evaluate,
    CoherenceEvaluator,
    RelevanceEvaluator,
    GroundednessEvaluator,
    SimilarityEvaluator
)

# Configure evaluators
evaluators = {
    "coherence": CoherenceEvaluator(model_config=judge_config),
    "relevance": RelevanceEvaluator(model_config=judge_config),
    "groundedness": GroundednessEvaluator(model_config=judge_config),
    "similarity": SimilarityEvaluator(model_config=judge_config)
}

# Run evaluation
result = evaluate(
    data="golden_dataset.jsonl",
    evaluators=evaluators
)
```

### Step 3.3: Compare Results

Run the same golden dataset through both GPT-4o and GPT-5.1:

1. Generate GPT-4o responses (baseline)
2. Generate GPT-5.1 responses
3. Evaluate both with Azure AI Foundry
4. Compare scores

**Acceptance criteria**:
- No metric should drop more than 10%
- Review any failing test cases manually
- Get business stakeholder sign-off

### Step 3.4: Shadow Testing

Once evaluations pass, run shadow testing:

```python
def handle_request(user_message, context):
    # Generate responses from both models
    gpt4o_response = call_gpt4o(user_message, context)
    gpt51_response = call_gpt51(user_message, context)
    
    # Log for comparison (don't serve GPT-5.1 yet)
    log_comparison(gpt4o_response, gpt51_response)
    
    # Only serve GPT-4o to users
    return gpt4o_response
```

Run for at least 1 week to catch edge cases.

---

## Phase 4: Production Rollout (Weeks 4-6)

### Step 4.1: Canary Deployment

Start with 5% of traffic:

```python
import random

def get_model():
    if random.random() < 0.05:  # 5% canary
        return "gpt-5.1"
    return "gpt-4o"
```

Monitor for 24-48 hours:
- Error rates
- Latency (p50, p95, p99)
- Quality metrics
- User feedback

### Step 4.2: Progressive Rollout

If canary is healthy, increase gradually:

| Day | Traffic % | Duration |
|-----|-----------|----------|
| 1-2 | 5% | Monitor closely |
| 3-4 | 25% | Check metrics |
| 5-6 | 50% | Validate at scale |
| 7+ | 100% | Full migration |

### Step 4.3: PTU Migration (if applicable)

For PTU deployments, you have two options:

**Option A: In-Place Migration** (faster, no rollback)
```bash
# Update existing deployment
az cognitiveservices account deployment update \
  --name <resource> \
  --resource-group <rg> \
  --deployment-name <deployment> \
  --model-name gpt-5.1 \
  --model-version 2025-11-13
```

**Option B: Multi-Deployment** (safer, has rollback)
1. Create new GPT-5.1 deployment
2. Route traffic gradually
3. Keep GPT-4o for rollback
4. Delete GPT-4o after verification

---

## Phase 5: Post-Migration (Ongoing)

### Step 5.1: Enable Continuous Monitoring

Set up ongoing evaluation sampling:

```python
# Sample 5% of production traffic for evaluation
if random.random() < 0.05:
    run_quality_evaluation(request, response)
```

### Step 5.2: Set Up Alerts

In Azure Monitor, create alerts for:
- Error rate increase > 5%
- Latency p95 increase > 20%
- Quality score drop > 10%

### Step 5.3: Document and Share

- Document any prompt changes made
- Share learnings with your team
- Update runbooks for the new model

---

## Rollback Procedure

If issues occur:

### For Standard Deployments
```bash
# Redeploy GPT-4o (if before retirement date)
az cognitiveservices account deployment create \
  --name <resource> \
  --resource-group <rg> \
  --deployment-name <deployment> \
  --model-name gpt-4o \
  --model-version 2024-11-20
```

### For PTU (Multi-Deployment)
- Switch traffic back to GPT-4o deployment via load balancer or application code

### For PTU (In-Place)
- Requires another in-place migration (20-30 min downtime)

---

## Need Help?

- Review the [FAQ](faq.md) for common questions
- Contact your Microsoft Customer Success team
- Open an issue in this repository

---

*Next: [API Changes Reference](api-changes.md)*
