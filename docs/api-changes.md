# API Changes Reference: GPT-4o to GPT-5.1

This document provides a complete reference of all API changes between GPT-4o and GPT-5.1.

## Summary of Changes

| Category | Change Type | Impact |
|----------|-------------|--------|
| Parameters removed | Breaking | Code will error without updates |
| Parameters renamed | Breaking | Code will error without updates |
| Parameters added | Non-breaking | Optional, but recommended |
| Role changes | Non-breaking | Works, but deprecated |
| API version | Required | Must update for new features |

---

## Parameters Removed

These parameters are **no longer supported** and will cause HTTP 400 errors if included:

### `temperature`

```python
# ❌ GPT-4o (will fail with GPT-5.1)
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages,
    temperature=0.7  # ERROR: Parameter not supported
)

# ✅ GPT-5.1
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages,
    reasoning_effort="low"  # Use this instead for behavior control
)
```

**Migration strategy**: Remove `temperature` and consider using `reasoning_effort` to control response behavior.

### `top_p`

```python
# ❌ Will fail
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages,
    top_p=0.95  # ERROR
)

# ✅ Simply remove
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages
)
```

### `frequency_penalty`

```python
# ❌ Will fail
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages,
    frequency_penalty=0.3  # ERROR
)

# ✅ Simply remove
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages
)
```

### `presence_penalty`

```python
# ❌ Will fail
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages,
    presence_penalty=0.1  # ERROR
)

# ✅ Simply remove
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages
)
```

### `logprobs` and `top_logprobs`

```python
# ❌ Will fail
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages,
    logprobs=True,      # ERROR
    top_logprobs=5      # ERROR
)

# ✅ Remove - these features are not available
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages
)
```

---

## Parameters Renamed

### `max_tokens` → `max_completion_tokens`

This is a **breaking change** with important behavioral differences:

```python
# ❌ GPT-4o style (will fail)
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages,
    max_tokens=500  # ERROR: Use max_completion_tokens
)

# ✅ GPT-5.1 style
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages,
    max_completion_tokens=500  # Correct
)
```

> ⚠️ **Important**: `max_completion_tokens` includes **reasoning tokens** (invisible in response). When using `reasoning_effort` > "none", the model may use some tokens for internal reasoning before generating visible output.

**Budget accordingly**:
- If you need 500 tokens of visible output
- And using `reasoning_effort="medium"`
- Consider setting `max_completion_tokens=800` or higher

---

## Parameters Added

### `reasoning_effort`

New parameter to control the model's reasoning depth:

```python
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages,
    max_completion_tokens=500,
    reasoning_effort="low"  # "none", "low", "medium", "high"
)
```

| Value | Description | Use Case | Cost Impact |
|-------|-------------|----------|-------------|
| `"none"` | No reasoning, immediate response | Simple tasks, classification | Lowest |
| `"low"` | Light reasoning | Most conversations | Low |
| `"medium"` | Moderate analysis | Complex questions | Medium |
| `"high"` | Deep reasoning | Critical analysis | Highest |

**Default is `"none"`** — this is important! If your GPT-4o responses were more detailed, you may need to explicitly set `"low"` or `"medium"`.

### `verbosity` (optional)

Controls output length:

```python
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages,
    max_completion_tokens=500,
    verbosity="medium"  # "low", "medium", "high"
)
```

---

## Role Changes

### `system` → `developer`

The `system` role is deprecated but still works. Microsoft recommends using `developer`:

```python
# ⚠️ Legacy (still works)
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello"}
]

# ✅ Recommended
messages = [
    {"role": "developer", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello"}
]
```

**Why the change?** The `developer` role more clearly indicates its purpose — instructions from the developer, not the system itself.

> ⚠️ **Don't use both**: If you include both `system` and `developer` roles, behavior may be unpredictable. Choose one.

---

## API Version Update

Update your API version to access GPT-5.1 features:

```python
# ❌ Old version
client = AzureOpenAI(
    api_version="2024-10-21",
    azure_endpoint=endpoint,
    api_key=api_key
)

# ✅ New version
client = AzureOpenAI(
    api_version="2025-06-01",
    azure_endpoint=endpoint,
    api_key=api_key
)
```

---

## Complete Before/After Example

### GPT-4o Code (Before)

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2024-10-21",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"]
)

def get_response(user_message: str, context: dict) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""You are a helpful customer service agent.
                Customer: {context.get('name')}
                Plan: {context.get('plan')}"""
            },
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0.3,
        max_tokens=500
    )
    return response.choices[0].message.content
```

### GPT-5.1 Code (After)

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2025-06-01",  # Updated
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"]
)

def get_response(user_message: str, context: dict) -> str:
    response = client.chat.completions.create(
        model="gpt-5.1",  # Updated
        messages=[
            {
                "role": "developer",  # Changed from system
                "content": f"""You are a helpful customer service agent.
                Customer: {context.get('name')}
                Plan: {context.get('plan')}"""
            },
            {"role": "user", "content": user_message}
        ],
        # Removed: temperature, top_p, frequency_penalty
        max_completion_tokens=500,  # Renamed from max_tokens
        reasoning_effort="low"  # Added for thoughtful responses
    )
    return response.choices[0].message.content
```

---

## SDK-Specific Notes

### Python SDK

Update to latest version:
```bash
pip install --upgrade openai
```

### JavaScript/TypeScript SDK

Update to latest version:
```bash
npm install openai@latest
```

### .NET SDK

Update to latest version:
```bash
dotnet add package Azure.AI.OpenAI
```

---

## Error Messages Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `400: temperature not supported` | Using `temperature` parameter | Remove it |
| `400: max_tokens not supported` | Using `max_tokens` parameter | Change to `max_completion_tokens` |
| `400: top_p not supported` | Using `top_p` parameter | Remove it |
| `404: model not found` | Model name wrong or not deployed | Check deployment name |

---

## Migration Checklist

Use this checklist when updating your code:

- [ ] Update `api_version` to `"2025-06-01"`
- [ ] Change model name to `"gpt-5.1"`
- [ ] Remove `temperature` parameter
- [ ] Remove `top_p` parameter
- [ ] Remove `frequency_penalty` parameter
- [ ] Remove `presence_penalty` parameter
- [ ] Change `max_tokens` to `max_completion_tokens`
- [ ] Change `role: "system"` to `role: "developer"`
- [ ] Add `reasoning_effort` parameter (recommended)
- [ ] Test with your golden dataset
- [ ] Compare quality metrics

---

*Next: [Evaluation Guide](evaluation-guide.md)*
