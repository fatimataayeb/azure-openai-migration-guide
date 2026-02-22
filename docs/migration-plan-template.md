# Migration Plan Template: GPT-4o to GPT-5.1

> Use this template to create your organization's migration plan. Customize based on your architecture and data sources.

---

## Table of Contents

1. [Pre-Migration Assessment](#1-pre-migration-assessment)
2. [Typical Environment Architecture](#2-typical-environment-architecture)
3. [Preparing Your Golden Dataset](#3-preparing-your-golden-dataset)
4. [Code Changes by Architecture](#4-code-changes-by-architecture)
5. [Testing & Validation](#5-testing--validation)
6. [Rollout Strategy](#6-rollout-strategy)
7. [PTU Migration Deep Dive](#7-ptu-migration-deep-dive)

---

## 1. Pre-Migration Assessment

### 1.1 Inventory Your Deployments

| Deployment Name | Resource Type | Region | Deployment Type | Applications Using It |
|-----------------|---------------|--------|-----------------|----------------------|
| *example: gpt4o-prod* | *Azure OpenAI* | *East US* | *PTU* | *Customer Service Bot* |
| | | | | |
| | | | | |

### 1.2 Identify Your Architecture

Check which architecture pattern(s) you're using:

- [ ] **Direct Azure OpenAI Resource** - Applications call Azure OpenAI endpoints directly
- [ ] **AI Hub Gateway Accelerator (APIM)** - Applications call through Azure API Management
- [ ] **Azure AI Foundry** - Applications use AI Foundry projects/deployments
- [ ] **LangChain/Semantic Kernel** - Using orchestration frameworks
- [ ] **Custom Gateway/Proxy** - Internal API layer in front of Azure OpenAI

### 1.3 Identify Your Deployment Types

Understanding your deployment types is critical as they have different migration timelines and approaches:

| Environment | Typical Deployment Type | Auto-Upgrade | Retirement Date | Migration Approach |
|-------------|------------------------|--------------|-----------------|-------------------|
| Development | Standard (PayGo) | March 9, 2026 | March 31, 2026 | Test migration first here |
| Staging/QA | Standard (PayGo) | March 9, 2026 | March 31, 2026 | Validate after Dev |
| Production | PTU (Provisioned) | No auto-upgrade | October 1, 2026 | In-place or Multi-deployment |

### 1.4 Identify Your Logging/Data Sources

Check where your request/response data is stored:

- [ ] **Azure Cosmos DB** - Application logs stored in Cosmos
- [ ] **Azure Monitor / Log Analytics** - Using diagnostic settings
- [ ] **Application Insights** - Telemetry data
- [ ] **Azure Data Lake / Blob Storage** - Exported logs
- [ ] **APIM Analytics** - API Management logging
- [ ] **Custom Database** - SQL, PostgreSQL, etc.
- [ ] **No Logging Currently** - Need to set up

---

## 2. Typical Environment Architecture

Most organizations use a combination of Standard (PayGo) and PTU (Provisioned) deployments:

### 2.1 Common Architecture Pattern

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DEVELOPMENT ENVIRONMENT                            │
│  ┌─────────────┐     ┌──────────────────────────────────────────────────┐   │
│  │ Application │ ──► │ Azure OpenAI - Standard (PayGo)                  │   │
│  │   (Dev)     │     │ • gpt-4o deployment                              │   │
│  └─────────────┘     │ • Pay-per-token                                  │   │
│                      │ • Auto-upgrades March 9, 2026                    │   │
│                      └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           STAGING/QA ENVIRONMENT                             │
│  ┌─────────────┐     ┌──────────────────────────────────────────────────┐   │
│  │ Application │ ──► │ Azure OpenAI - Standard (PayGo)                  │   │
│  │  (Staging)  │     │ • gpt-4o deployment                              │   │
│  └─────────────┘     │ • Pay-per-token                                  │   │
│                      │ • Auto-upgrades March 9, 2026                    │   │
│                      └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRODUCTION ENVIRONMENT                             │
│  ┌─────────────┐     ┌──────────────────────────────────────────────────┐   │
│  │ Application │ ──► │ Azure OpenAI - PTU (Provisioned)                 │   │
│  │   (Prod)    │     │ • gpt-4o deployment                              │   │
│  └─────────────┘     │ • Reserved capacity (PTUs)                       │   │
│                      │ • NO auto-upgrade (manual migration required)    │   │
│                      │ • Retirement: October 1, 2026                    │   │
│                      └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Migration Timeline by Environment

```
                    Jan 2026        Mar 9         Mar 31        Oct 1
                        │              │              │             │
    DEV (PayGo)         │──── Test ────│►Auto-upgrade │►Retired     │
                        │              │              │             │
    STAGING (PayGo)     │──── Test ────│►Auto-upgrade │►Retired     │
                        │              │              │             │
    PROD (PTU)          │─────────── Manual Migration Window ───────│►Retired
                        │              │              │             │
                    Start here!    Use auto-upgrade   Standard    PTU
                                   to test in Dev    deadline    deadline
```

### 2.3 Recommended Migration Sequence

| Phase | Environment | Action | Timeline |
|-------|-------------|--------|----------|
| 1 | Development (PayGo) | Update code, run evaluations | Before March 9 |
| 2 | Development (PayGo) | Let auto-upgrade happen, validate | March 9+ |
| 3 | Staging (PayGo) | Deploy updated code, validate with auto-upgraded model | After Dev validation |
| 4 | Production (PTU) | Migrate using chosen PTU strategy (see Section 7) | After Staging validation |

> **Key Insight**: Use the March 9 auto-upgrade in Dev/Staging as a free "test run" before manually migrating Production PTU.

### 2.4 Why This Pattern Works

1. **Dev/Staging auto-upgrade is your safety net** — If something breaks, you discover it in non-production first
2. **PTU has longer timeline** — October 1 deadline gives you months to validate after Standard environments migrate
3. **Cost efficiency** — No need to provision PTU for testing; use PayGo environments
4. **No rollback after retirement** — Once GPT-4o is retired, there's no going back. This is why thorough testing in Dev/Staging before PTU migration is critical

---

## 3. Preparing Your Golden Dataset

### 2.1 Dataset Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Total test cases | 50 | 100-200 |
| Cases per category | 10 | 20-30 |
| Languages covered | All supported | All supported |
| Edge cases | 10% | 15-20% |

### 2.2 Extracting Data from Cosmos DB

If you're logging requests/responses to Cosmos DB:

```python
"""
Extract golden dataset from Cosmos DB logs.
Assumes your container stores documents with query/response fields.
"""
from azure.cosmos import CosmosClient
import json
import random

# Connect to Cosmos DB
client = CosmosClient(
    url="https://your-account.documents.azure.com:443/",
    credential="your-key-or-use-managed-identity"
)

database = client.get_database_client("your-database")
container = database.get_container_client("your-logs-container")

def extract_golden_dataset(
    sample_size: int = 100,
    categories: list = None,
    date_from: str = None
):
    """
    Extract diverse samples from Cosmos DB logs.

    Adjust the query based on your document schema.
    """

    # Build query - adjust field names to match your schema
    query = """
    SELECT
        c.id,
        c.timestamp,
        c.user_query as query,
        c.model_response as response,
        c.context,
        c.category,
        c.language,
        c.customer_id
    FROM c
    WHERE c.model = 'gpt-4o'
    """

    if date_from:
        query += f" AND c.timestamp >= '{date_from}'"

    if categories:
        cats = ", ".join([f"'{c}'" for c in categories])
        query += f" AND c.category IN ({cats})"

    query += " ORDER BY c.timestamp DESC"

    # Execute query
    items = list(container.query_items(query, enable_cross_partition_query=True))

    print(f"Found {len(items)} matching records")

    # Sample by category for diversity
    by_category = {}
    for item in items:
        cat = item.get('category', 'unknown')
        by_category.setdefault(cat, []).append(item)

    # Take proportional samples from each category
    samples = []
    per_category = max(10, sample_size // len(by_category)) if by_category else sample_size

    for cat, cat_items in by_category.items():
        cat_sample = random.sample(cat_items, min(per_category, len(cat_items)))
        samples.extend(cat_sample)

    # Shuffle and limit
    random.shuffle(samples)
    samples = samples[:sample_size]

    return samples

def format_for_evaluation(samples: list, output_path: str):
    """
    Format extracted samples into golden dataset JSONL.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, sample in enumerate(samples):
            # Create test case - adjust field mapping as needed
            test_case = {
                "test_id": f"{sample.get('category', 'GEN')}_{i:03d}",
                "query": sample.get('query', ''),
                "context": sample.get('context', ''),
                "ground_truth": sample.get('response', ''),  # GPT-4o response as baseline
                "category": sample.get('category', 'general'),
                "language": sample.get('language', 'en'),
                "source_id": sample.get('id', '')  # Original record ID for traceability
            }
            f.write(json.dumps(test_case, ensure_ascii=False) + '\n')

    print(f"Created golden dataset: {output_path} ({len(samples)} cases)")

# Usage
samples = extract_golden_dataset(
    sample_size=100,
    categories=['billing', 'technical', 'general', 'complaints'],
    date_from='2025-01-01'
)

format_for_evaluation(samples, 'golden_dataset.jsonl')
```

### 2.3 Extracting Data from Log Analytics

If you're using Azure Monitor diagnostic settings:

```kusto
// KQL Query to extract GPT-4o interactions from Log Analytics
// Run this in your Log Analytics workspace

AzureDiagnostics
| where ResourceProvider == "MICROSOFT.COGNITIVESERVICES"
| where Category == "RequestResponse"
| where Model_s == "gpt-4o"
| where TimeGenerated > ago(30d)
| extend RequestBody = parse_json(RequestBody_s)
| extend ResponseBody = parse_json(ResponseBody_s)
| extend UserQuery = tostring(RequestBody.messages[-1].content)
| extend ModelResponse = tostring(ResponseBody.choices[0].message.content)
| project
    TimeGenerated,
    UserQuery,
    ModelResponse,
    DurationMs_d,
    OperationName
| take 500
```

Export results to CSV, then convert to JSONL:

```python
"""Convert Log Analytics CSV export to golden dataset JSONL."""
import csv
import json

def csv_to_golden_dataset(csv_path: str, output_path: str):
    with open(csv_path, 'r', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)

        with open(output_path, 'w', encoding='utf-8') as f_out:
            for i, row in enumerate(reader):
                test_case = {
                    "test_id": f"LOG_{i:04d}",
                    "query": row.get('UserQuery', ''),
                    "ground_truth": row.get('ModelResponse', ''),
                    "context": "",
                    "category": "general"
                }
                f_out.write(json.dumps(test_case, ensure_ascii=False) + '\n')

csv_to_golden_dataset('log_analytics_export.csv', 'golden_dataset.jsonl')
```

### 2.4 Extracting from Application Insights

```python
"""Extract from Application Insights using the Query API."""
from azure.monitor.query import LogsQueryClient
from azure.identity import DefaultAzureCredential
import json

credential = DefaultAzureCredential()
client = LogsQueryClient(credential)

workspace_id = "your-workspace-id"

query = """
customEvents
| where name == "OpenAI_Request"
| where customDimensions.model == "gpt-4o"
| extend query = tostring(customDimensions.user_query)
| extend response = tostring(customDimensions.model_response)
| extend category = tostring(customDimensions.category)
| project timestamp, query, response, category
| take 200
"""

response = client.query_workspace(workspace_id, query, timespan="P30D")

# Convert to golden dataset
with open('golden_dataset.jsonl', 'w') as f:
    for i, row in enumerate(response.tables[0].rows):
        test_case = {
            "test_id": f"APPINS_{i:04d}",
            "query": row[1],
            "ground_truth": row[2],
            "category": row[3] or "general"
        }
        f.write(json.dumps(test_case, ensure_ascii=False) + '\n')
```

### 2.5 No Existing Logs? Start Logging Now

If you don't have historical data, add logging immediately:

```python
"""Simple logging wrapper to start collecting data."""
import json
import logging
from datetime import datetime
from azure.cosmos import CosmosClient

# Or use any storage: Blob, SQL, file system, etc.
cosmos_client = CosmosClient(url, credential)
container = cosmos_client.get_database_client("logs").get_container_client("openai_requests")

def log_openai_interaction(query: str, response: str, context: dict = None, category: str = None):
    """Log each interaction for future dataset creation."""
    log_entry = {
        "id": f"{datetime.utcnow().isoformat()}_{hash(query) % 10000}",
        "timestamp": datetime.utcnow().isoformat(),
        "user_query": query,
        "model_response": response,
        "context": json.dumps(context) if context else "",
        "category": category,
        "model": "gpt-4o"
    }
    container.create_item(log_entry)

# Use in your application
def get_ai_response(user_message: str, context: dict):
    response = client.chat.completions.create(...)
    response_text = response.choices[0].message.content

    # Log for future golden dataset
    log_openai_interaction(user_message, response_text, context, category="customer_service")

    return response_text
```

---

## 4. Code Changes by Architecture

### 3.1 Direct Azure OpenAI Resource

**Before (GPT-4o):**
```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2024-10-21",
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_key=os.environ["AZURE_OPENAI_API_KEY"]
)

response = client.chat.completions.create(
    model="gpt-4o",  # Your deployment name
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_input}
    ],
    temperature=0.7,
    top_p=0.95,
    max_tokens=500
)
```

**After (GPT-5.1):**
```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2025-06-01",  # Updated
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_key=os.environ["AZURE_OPENAI_API_KEY"]
)

response = client.chat.completions.create(
    model="gpt-51",  # Your new deployment name
    messages=[
        {"role": "developer", "content": "You are a helpful assistant."},  # Changed
        {"role": "user", "content": user_input}
    ],
    # Removed: temperature, top_p
    max_completion_tokens=500,  # Renamed
    reasoning_effort="low"  # New parameter
)
```

---

### 3.2 AI Hub Gateway Accelerator (APIM)

If you're using the [AI Hub Gateway Accelerator](https://github.com/Azure-Samples/ai-hub-gateway-solution-accelerator), your applications call through APIM.

**Architecture:**
```
Application → APIM (ai-hub-gateway) → Azure OpenAI Backend Pool
```

**Configuration Changes Needed:**

#### Option A: Update at APIM Policy Level (Recommended)

Modify your APIM inbound policy to transform requests:

```xml
<!-- APIM Inbound Policy: Transform GPT-4o requests to GPT-5.1 -->
<inbound>
    <base />

    <!-- Transform request body for GPT-5.1 compatibility -->
    <set-body>@{
        var body = context.Request.Body.As<JObject>(preserveContent: true);

        // Update model if specified
        if (body["model"]?.ToString() == "gpt-4o") {
            body["model"] = "gpt-5.1";
        }

        // Transform messages: system -> developer
        var messages = body["messages"] as JArray;
        if (messages != null) {
            foreach (var msg in messages) {
                if (msg["role"]?.ToString() == "system") {
                    msg["role"] = "developer";
                }
            }
        }

        // Rename max_tokens to max_completion_tokens
        if (body["max_tokens"] != null) {
            body["max_completion_tokens"] = body["max_tokens"];
            body.Remove("max_tokens");
        }

        // Remove unsupported parameters
        body.Remove("temperature");
        body.Remove("top_p");
        body.Remove("frequency_penalty");
        body.Remove("presence_penalty");
        body.Remove("logprobs");
        body.Remove("top_logprobs");

        // Add reasoning_effort if not present
        if (body["reasoning_effort"] == null) {
            body["reasoning_effort"] = "low";
        }

        return body.ToString();
    }</set-body>

    <!-- Update API version in query string -->
    <set-query-parameter name="api-version" exists-action="override">
        <value>2025-06-01</value>
    </set-query-parameter>
</inbound>
```

#### Option B: Update at Application Level

If you prefer to update applications individually:

**Before (calling APIM gateway):**
```python
import requests

APIM_ENDPOINT = "https://your-apim.azure-api.net/openai"
APIM_KEY = os.environ["APIM_SUBSCRIPTION_KEY"]

def call_openai_via_apim(user_message: str):
    response = requests.post(
        f"{APIM_ENDPOINT}/deployments/gpt-4o/chat/completions",
        headers={
            "Ocp-Apim-Subscription-Key": APIM_KEY,
            "Content-Type": "application/json"
        },
        params={"api-version": "2024-10-21"},
        json={
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
    )
    return response.json()
```

**After (calling APIM gateway):**
```python
import requests

APIM_ENDPOINT = "https://your-apim.azure-api.net/openai"
APIM_KEY = os.environ["APIM_SUBSCRIPTION_KEY"]

def call_openai_via_apim(user_message: str):
    response = requests.post(
        f"{APIM_ENDPOINT}/deployments/gpt-51/chat/completions",  # Updated deployment
        headers={
            "Ocp-Apim-Subscription-Key": APIM_KEY,
            "Content-Type": "application/json"
        },
        params={"api-version": "2025-06-01"},  # Updated
        json={
            "messages": [
                {"role": "developer", "content": "You are a helpful assistant."},  # Changed
                {"role": "user", "content": user_message}
            ],
            # Removed: temperature
            "max_completion_tokens": 500,  # Renamed
            "reasoning_effort": "low"  # Added
        }
    )
    return response.json()
```

#### APIM Backend Pool Update

Update your backend pool to use GPT-5.1 deployments:

```json
{
    "backends": [
        {
            "name": "openai-eastus",
            "url": "https://your-aoai-eastus.openai.azure.com/",
            "deployment": "gpt-51",
            "priority": 1
        },
        {
            "name": "openai-westus",
            "url": "https://your-aoai-westus.openai.azure.com/",
            "deployment": "gpt-51",
            "priority": 2
        }
    ]
}
```

---

### 3.3 Azure AI Foundry

If you're using Azure AI Foundry (formerly Azure AI Studio) projects:

**Before (GPT-4o with AI Foundry):**
```python
from azure.ai.inference import ChatCompletionsClient
from azure.identity import DefaultAzureCredential

# AI Foundry project endpoint
client = ChatCompletionsClient(
    endpoint="https://your-project.region.inference.ai.azure.com",
    credential=DefaultAzureCredential()
)

response = client.complete(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_input}
    ],
    temperature=0.7,
    max_tokens=500
)
```

**After (GPT-5.1 with AI Foundry):**
```python
from azure.ai.inference import ChatCompletionsClient
from azure.identity import DefaultAzureCredential

# AI Foundry project endpoint
client = ChatCompletionsClient(
    endpoint="https://your-project.region.inference.ai.azure.com",
    credential=DefaultAzureCredential()
)

response = client.complete(
    model="gpt-5.1",  # Updated
    messages=[
        {"role": "developer", "content": "You are a helpful assistant."},  # Changed
        {"role": "user", "content": user_input}
    ],
    # Removed: temperature
    max_tokens=500,  # Note: AI Foundry SDK may still use max_tokens
    extra_params={
        "reasoning_effort": "low"  # Pass new parameters via extra_params
    }
)
```

**Using OpenAI SDK with AI Foundry:**
```python
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    api_version="2025-06-01",
    azure_endpoint="https://your-project.region.inference.ai.azure.com",
    azure_ad_token_provider=token_provider
)

response = client.chat.completions.create(
    model="gpt-5.1",
    messages=[
        {"role": "developer", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_input}
    ],
    max_completion_tokens=500,
    reasoning_effort="low"
)
```

---

### 3.4 LangChain Integration

**Before (GPT-4o):**
```python
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    azure_deployment="gpt-4o",
    api_version="2024-10-21",
    temperature=0.7,
    max_tokens=500
)
```

**After (GPT-5.1):**
```python
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    azure_deployment="gpt-51",
    api_version="2025-06-01",
    max_tokens=500,  # LangChain may handle the parameter name mapping
    model_kwargs={
        "reasoning_effort": "low"
    }
)

# Note: You may need to update system message handling in your chains
# to use "developer" role instead of "system"
```

---

### 3.5 Semantic Kernel Integration

**Before (GPT-4o):**
```csharp
using Microsoft.SemanticKernel;

var builder = Kernel.CreateBuilder();
builder.AddAzureOpenAIChatCompletion(
    deploymentName: "gpt-4o",
    endpoint: azureOpenAIEndpoint,
    apiKey: azureOpenAIKey
);

var kernel = builder.Build();
```

**After (GPT-5.1):**
```csharp
using Microsoft.SemanticKernel;

var builder = Kernel.CreateBuilder();
builder.AddAzureOpenAIChatCompletion(
    deploymentName: "gpt-51",
    endpoint: azureOpenAIEndpoint,
    apiKey: azureOpenAIKey,
    apiVersion: "2025-06-01"  // Specify new API version
);

var kernel = builder.Build();

// When invoking, use execution settings
var settings = new AzureOpenAIPromptExecutionSettings
{
    MaxTokens = 500,
    // Temperature not supported - remove it
    ExtensionData = new Dictionary<string, object>
    {
        ["reasoning_effort"] = "low"
    }
};
```

---

## 5. Testing & Validation

### 5.1 Run Audit Script

```bash
# Find all code that needs updating
python scripts/audit_codebase.py --path /your/application/code

# Export as JSON for tracking
python scripts/audit_codebase.py --path /your/code --format json --output audit_report.json
```

### 5.2 Run Evaluation

```bash
# Set credentials
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-key"

# Run comparison
python scripts/run_evaluation.py \
    --dataset golden_dataset.jsonl \
    --gpt4o-deployment gpt-4o \
    --gpt51-deployment gpt-51 \
    --output evaluation_results.json
```

### 5.3 Quality Gates

| Metric | Minimum Score | Max Regression |
|--------|---------------|----------------|
| Coherence | 4.0 | -10% |
| Fluency | 4.0 | -10% |
| Relevance | 4.0 | -10% |
| Groundedness | 3.5 | -10% |
| Similarity | 3.5 | -15% |

### 5.4 Sign-off Checklist

- [ ] All HIGH severity audit items resolved
- [ ] Golden dataset created (minimum 50 cases)
- [ ] Evaluation run completed
- [ ] No quality regressions > 10%
- [ ] Manual review of 10+ response comparisons
- [ ] Stakeholder approval obtained

---

## 6. Rollout Strategy

### 6.1 For Standard Deployments

```
Week 1: Development environment
   └── Update code → Run evaluations → Fix issues

Week 2: Staging/QA environment
   └── Deploy → Validate → Shadow testing

Week 3-4: Production (gradual)
   └── 5% → 25% → 50% → 100%
```

### 6.2 For PTU Deployments (Summary)

**Option A: Blue-Green Deployment**
```
1. Create new GPT-5.1 PTU deployment
2. Update application config to use new deployment
3. Route traffic gradually via load balancer
4. Monitor for 1 week
5. Decommission GPT-4o PTU
```

**Option B: In-Place Migration**
```
1. Schedule maintenance window
2. Update deployment model version
3. Validate immediately after
4. Note: No rollback after Oct 1, 2026 retirement
```

> See [Section 7: PTU Migration Deep Dive](#7-ptu-migration-deep-dive) for detailed guidance on choosing between these options.

### 6.3 Traffic Splitting Example

```python
import random
import os

def get_model_config():
    """Return model configuration based on rollout percentage."""

    rollout_percentage = float(os.environ.get("GPT51_ROLLOUT_PCT", "0"))

    if random.random() * 100 < rollout_percentage:
        return {
            "deployment": "gpt-51",
            "api_version": "2025-06-01",
            "use_new_params": True
        }
    else:
        return {
            "deployment": "gpt-4o",
            "api_version": "2024-10-21",
            "use_new_params": False
        }
```

---

## 7. PTU Migration Deep Dive

PTU (Provisioned Throughput Units) deployments require manual migration and have different considerations than Standard deployments.

### 7.1 Understanding Your Options

| Option | In-Place Migration | Multi-Deployment (Side-by-Side) |
|--------|-------------------|--------------------------------|
| **How it works** | Update existing deployment to GPT-5.1 | Create new GPT-5.1 deployment alongside GPT-4o |
| **Downtime** | ~20-30 minutes during migration | Zero downtime |
| **Rollback before retirement** | Yes, re-migrate to GPT-4o (~20-30 min) | Yes, switch traffic back to GPT-4o |
| **Rollback after retirement** | No - GPT-4o retired | No - GPT-4o retired |
| **Cost during migration** | Same PTU cost | Double PTU cost temporarily |
| **Risk level** | Higher (all-or-nothing) | Lower (gradual traffic shift) |
| **Best for** | Cost-sensitive, confident in testing | Risk-averse, production-critical |

### 7.2 Option A: In-Place Migration (Detailed)

In-place migration updates your existing PTU deployment from GPT-4o to GPT-5.1.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         IN-PLACE MIGRATION                          │
│                                                                     │
│   BEFORE                              AFTER                         │
│   ┌─────────────────┐                ┌─────────────────┐           │
│   │ PTU Deployment  │    migrate     │ PTU Deployment  │           │
│   │ gpt-4o          │ ─────────────► │ gpt-5.1         │           │
│   │ 100 PTUs        │   (~20-30min)  │ 100 PTUs        │           │
│   └─────────────────┘                └─────────────────┘           │
│                                                                     │
│   • Same deployment name                                            │
│   • Same endpoint URL                                               │
│   • Application code must be updated BEFORE migration               │
└─────────────────────────────────────────────────────────────────────┘
```

**Steps:**

```bash
# 1. Ensure application code is updated for GPT-5.1 parameters

# 2. Schedule maintenance window (20-30 minutes)

# 3. Execute in-place migration
az cognitiveservices account deployment create \
  --name <your-resource-name> \
  --resource-group <your-resource-group> \
  --deployment-name <existing-deployment-name> \
  --model-name gpt-5.1 \
  --model-version 2025-11-13 \
  --model-format OpenAI \
  --sku-capacity <your-ptu-count> \
  --sku-name ProvisionedManaged

# 4. Validate immediately after migration completes
python scripts/run_evaluation.py --dataset golden_dataset.jsonl

# 5. Monitor application logs and metrics
```

**When to choose In-Place:**
- You have thoroughly tested in Dev/Staging environments
- Cost is a concern (no double PTU billing)
- You can schedule a maintenance window
- Your application can tolerate ~20-30 min downtime

### 7.3 Option B: Multi-Deployment / Side-by-Side (Detailed)

Create a new GPT-5.1 PTU deployment while keeping GPT-4o running, then gradually shift traffic.

```
┌─────────────────────────────────────────────────────────────────────┐
│                      MULTI-DEPLOYMENT MIGRATION                     │
│                                                                     │
│   PHASE 1: Create new deployment                                    │
│   ┌─────────────────┐        ┌─────────────────┐                   │
│   │ PTU Deployment  │        │ PTU Deployment  │                   │
│   │ gpt-4o          │        │ gpt-5.1         │ ← NEW             │
│   │ 100 PTUs        │        │ 100 PTUs        │                   │
│   └────────┬────────┘        └────────┬────────┘                   │
│            │ 100%                     │ 0%                         │
│            └──────────┬───────────────┘                            │
│                       ▼                                             │
│                 ┌───────────┐                                       │
│                 │    App    │                                       │
│                 └───────────┘                                       │
│                                                                     │
│   PHASE 2: Gradual traffic shift                                    │
│   ┌─────────────────┐        ┌─────────────────┐                   │
│   │ gpt-4o          │        │ gpt-5.1         │                   │
│   │ 100 PTUs        │        │ 100 PTUs        │                   │
│   └────────┬────────┘        └────────┬────────┘                   │
│            │ 50%                      │ 50%                        │
│            └──────────┬───────────────┘                            │
│                       ▼                                             │
│                 ┌───────────┐                                       │
│                 │    App    │                                       │
│                 └───────────┘                                       │
│                                                                     │
│   PHASE 3: Complete migration                                       │
│   ┌─────────────────┐        ┌─────────────────┐                   │
│   │ gpt-4o          │        │ gpt-5.1         │                   │
│   │ DELETE          │        │ 100 PTUs        │                   │
│   └─────────────────┘        └────────┬────────┘                   │
│                                       │ 100%                       │
│                                       ▼                             │
│                                 ┌───────────┐                       │
│                                 │    App    │                       │
│                                 └───────────┘                       │
└─────────────────────────────────────────────────────────────────────┘
```

**Steps:**

```bash
# 1. Create new GPT-5.1 PTU deployment
az cognitiveservices account deployment create \
  --name <your-resource-name> \
  --resource-group <your-resource-group> \
  --deployment-name gpt51-prod \
  --model-name gpt-5.1 \
  --model-version 2025-11-13 \
  --model-format OpenAI \
  --sku-capacity <your-ptu-count> \
  --sku-name ProvisionedManaged

# 2. Update application to support both deployments (see code below)

# 3. Gradually shift traffic: 5% → 25% → 50% → 100%

# 4. After validation, delete old GPT-4o deployment
az cognitiveservices account deployment delete \
  --name <your-resource-name> \
  --resource-group <your-resource-group> \
  --deployment-name gpt4o-prod
```

**Application Code for Traffic Splitting:**

```python
import os
import random
from openai import AzureOpenAI

# Configuration
GPT51_TRAFFIC_PERCENT = float(os.environ.get("GPT51_TRAFFIC_PERCENT", "0"))

# Separate clients for each model
client_4o = AzureOpenAI(
    api_version="2024-10-21",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"]
)

client_51 = AzureOpenAI(
    api_version="2025-06-01",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"]
)

def get_response(user_message: str, context: dict) -> dict:
    """Route traffic between GPT-4o and GPT-5.1 based on configured percentage."""

    use_gpt51 = random.random() * 100 < GPT51_TRAFFIC_PERCENT

    if use_gpt51:
        # GPT-5.1 call
        response = client_51.chat.completions.create(
            model="gpt51-prod",  # New deployment
            messages=[
                {"role": "developer", "content": build_system_prompt(context)},
                {"role": "user", "content": user_message}
            ],
            max_completion_tokens=500,
            reasoning_effort="low"
        )
        model_used = "gpt-5.1"
    else:
        # GPT-4o call (legacy)
        response = client_4o.chat.completions.create(
            model="gpt4o-prod",  # Old deployment
            messages=[
                {"role": "system", "content": build_system_prompt(context)},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        model_used = "gpt-4o"

    return {
        "response": response.choices[0].message.content,
        "model": model_used  # Log this for monitoring
    }
```

**When to choose Multi-Deployment:**
- Zero downtime is required
- You want gradual rollout with easy rollback (before retirement)
- Production is business-critical
- Budget allows temporary double PTU cost

### 7.4 Cost Comparison

| Scenario | In-Place | Multi-Deployment |
|----------|----------|------------------|
| 100 PTUs, 2-week migration | 100 PTU cost | 200 PTU cost for 2 weeks |
| 100 PTUs, 4-week migration | 100 PTU cost | 200 PTU cost for 4 weeks |

> **Tip**: If using multi-deployment, minimize the overlap period to reduce costs. Complete validation quickly and delete the old deployment.

### 7.5 PTU Migration Decision Flowchart

```
                            ┌─────────────────────────┐
                            │ Can you schedule        │
                            │ 20-30 min downtime?     │
                            └───────────┬─────────────┘
                                        │
                          ┌─────────────┴─────────────┐
                          │                           │
                         YES                          NO
                          │                           │
                          ▼                           ▼
              ┌───────────────────────┐   ┌───────────────────────┐
              │ Have you thoroughly   │   │ Use Multi-Deployment  │
              │ tested in Dev/Staging?│   │ (Side-by-Side)        │
              └───────────┬───────────┘   └───────────────────────┘
                          │
            ┌─────────────┴─────────────┐
            │                           │
           YES                          NO
            │                           │
            ▼                           ▼
┌───────────────────────┐   ┌───────────────────────┐
│ Is cost a primary     │   │ Complete testing      │
│ concern?              │   │ first, then decide    │
└───────────┬───────────┘   └───────────────────────┘
            │
  ┌─────────┴─────────┐
  │                   │
 YES                  NO
  │                   │
  ▼                   ▼
┌─────────────┐   ┌───────────────────────┐
│ Use         │   │ Use Multi-Deployment  │
│ In-Place    │   │ for extra safety      │
└─────────────┘   └───────────────────────┘
```

### 7.6 PTU Migration Checklist

**Before Migration:**
- [ ] Code updated and deployed to handle GPT-5.1 parameters
- [ ] Golden dataset tested with GPT-5.1 in Dev/Staging (Standard)
- [ ] No quality regressions identified
- [ ] Stakeholder sign-off obtained
- [ ] Migration strategy decided (In-Place vs Multi-Deployment)
- [ ] Maintenance window scheduled (if In-Place)
- [ ] Monitoring and alerting configured

**During Migration:**
- [ ] Communication sent to stakeholders
- [ ] Migration executed per chosen strategy
- [ ] Immediate validation completed
- [ ] Application logs monitored for errors

**After Migration:**
- [ ] Quality metrics validated
- [ ] Performance metrics validated (latency, throughput)
- [ ] Old deployment deleted (if Multi-Deployment)
- [ ] Documentation updated
- [ ] Continuous monitoring enabled

---

## Appendix: Quick Reference

### Parameter Changes Summary

| Remove | Rename | Add |
|--------|--------|-----|
| `temperature` | `max_tokens` → `max_completion_tokens` | `reasoning_effort` |
| `top_p` | `"system"` role → `"developer"` role | `verbosity` (optional) |
| `frequency_penalty` | | |
| `presence_penalty` | | |
| `logprobs` | | |
| `top_logprobs` | | |

### reasoning_effort Values

| Value | Use Case | Token Usage |
|-------|----------|-------------|
| `"none"` | Classification, extraction, simple lookups | Lowest |
| `"low"` | Standard conversations, most use cases | Low |
| `"medium"` | Complex analysis, detailed reports | Medium |
| `"high"` | Critical decisions, deep reasoning | Highest |

### Key Dates

| Date | Event |
|------|-------|
| March 9, 2026 | Auto-upgrade begins (Standard) |
| March 31, 2026 | GPT-4o Standard retired |
| October 1, 2026 | GPT-4o PTU retired |

---

*Last updated: [Date]*
*Owner: [Team/Person]*
