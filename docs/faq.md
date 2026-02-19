# Frequently Asked Questions (FAQ)

## General Questions

### Why is Microsoft retiring GPT-4o?

Microsoft is evolving Azure OpenAI to bring you better capabilities. GPT-5.1 offers significant improvements including:
- Enhanced reasoning capabilities with adjustable depth
- Better instruction following for more predictable outputs
- Improved factual accuracy (~45% fewer hallucinations)
- Lower input token costs (50% reduction)

This is a natural evolution of the platform, similar to past model upgrades. Microsoft provides ample notice and support to ensure smooth transitions.

### What if I don't migrate?

| Deployment Type | What Happens |
|-----------------|--------------|
| Standard (PayGo) | Auto-upgrades March 9, 2026; retired March 31, 2026 |
| PTU (Provisioned) | Must manually migrate before October 1, 2026 |

After retirement dates, API calls to GPT-4o will return errors. We strongly recommend migrating proactively to avoid service disruption.

### Can I stay on GPT-4o longer?

For Standard deployments, you can set `versionUpgradeOption: "NoAutoUpgrade"` to prevent automatic upgrade, but the model will still be retired on March 31, 2026.

For PTU deployments, you have until October 1, 2026, giving you more time to test and migrate.

---

## Code Changes

### Why was `temperature` removed?

GPT-5.1 uses a different approach to controlling output variability. Instead of `temperature`, you now use:

- **`reasoning_effort`**: Controls how much the model "thinks" before responding
- More deterministic outputs by design
- Better consistency for production applications

If you need varied outputs, you can adjust your prompts or use the Responses API which offers additional controls.

### What's the difference between `max_tokens` and `max_completion_tokens`?

| Parameter | Model | What It Counts |
|-----------|-------|----------------|
| `max_tokens` | GPT-4o | Output tokens only |
| `max_completion_tokens` | GPT-5.1 | Output tokens + reasoning tokens |

> ⚠️ **Important**: In GPT-5.1, reasoning tokens (when `reasoning_effort` > "none") count against this limit but are invisible in the response. Budget accordingly.

### Do I have to change `system` to `developer`?

While `system` still works (for backward compatibility), Microsoft recommends using `developer` because:
- It's clearer about the role's purpose
- It's the standard going forward
- It avoids potential deprecation in future versions

```python
# Both work, but developer is recommended
{"role": "system", "content": "..."}    # ⚠️ Legacy
{"role": "developer", "content": "..."}  # ✅ Recommended
```

### What does `reasoning_effort` actually do?

It controls how much internal "thinking" the model does before responding:

| Value | Behavior | Best For |
|-------|----------|----------|
| `"none"` | No reasoning, direct response | Simple tasks, classification, extraction |
| `"low"` | Light reasoning | Standard conversations, most use cases |
| `"medium"` | Moderate reasoning | Complex analysis, detailed explanations |
| `"high"` | Deep reasoning | Critical decisions, multi-step problems |

**Default is `"none"`**, which may produce shallower responses than GPT-4o. If your responses seem less detailed, try `"low"` or `"medium"`.

---

## Quality & Testing

### My GPT-5.1 responses are shorter/shallower. Why?

This is the #1 reported issue. It's usually because `reasoning_effort` defaults to `"none"`. Try:

```python
# Add reasoning_effort
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=messages,
    max_completion_tokens=500,
    reasoning_effort="low"  # Add this
)
```

### The tone feels different (colder, less warm). How do I fix it?

GPT-5.1 is more precise and may feel less conversational by default. Solutions:

1. **Explicit personality instructions**:
```python
developer_message = """You are a friendly, warm customer service agent.
Personality traits:
- Warm and welcoming
- Use the customer's name
- Show empathy before solutions
- Conversational tone, not robotic"""
```

2. **Use `reasoning_effort="low"`** or higher for more thoughtful responses

3. **Review your prompts** for any instructions that might conflict (GPT-5.1 follows instructions more precisely)

### How do I know if quality is acceptable?

Use Azure AI Foundry evaluations with these metrics:

| Metric | Good Score | Concern Threshold |
|--------|------------|-------------------|
| Coherence | 4.0+ | Below 3.5 |
| Relevance | 4.0+ | Below 3.5 |
| Groundedness | 4.0+ | Below 3.5 |
| Similarity | 3.5+ | Below 3.0 |

Compare GPT-5.1 scores to GPT-4o baseline. Flag any metric that drops more than 10%.

### How many test cases do I need?

| Scenario | Minimum | Recommended |
|----------|---------|-------------|
| Simple application | 30 | 50 |
| Multiple use cases | 50 | 100 |
| Complex/critical app | 100 | 200+ |

Include edge cases, multiple languages, and difficult scenarios.

---

## Deployment & Operations

### What's the recommended rollout strategy?

```
Week 1-2: Code changes + evaluation testing
Week 3:   Shadow testing (both models, serve only GPT-4o)
Week 4:   Canary (5% traffic to GPT-5.1)
Week 5:   Progressive rollout (25% → 50% → 100%)
Week 6+:  Monitor and optimize
```

### Can I run both models simultaneously?

Yes! This is recommended during migration:

```python
def get_response(user_input, use_new_model=False):
    if use_new_model:
        return call_gpt51(user_input)
    return call_gpt4o(user_input)

# Use feature flags or traffic splitting
model_choice = "gpt-5.1" if random.random() < 0.05 else "gpt-4o"
```

### How do I rollback if something goes wrong?

**For Standard deployments** (before retirement):
```bash
az cognitiveservices account deployment update \
  --name <resource> --resource-group <rg> \
  --deployment-name <name> \
  --model-name gpt-4o \
  --model-version 2024-11-20
```

**For PTU (multi-deployment)**:
- Keep GPT-4o deployment running during migration
- Switch traffic back via load balancer or code

**For PTU (in-place)**:
- Requires another in-place migration (~20-30 min)

---

## Cost & Performance

### Will GPT-5.1 cost more?

**Input tokens**: 50% cheaper ($1.25/M vs $2.50/M) ✅

**Output tokens**: Same price ($10/M)

**But watch out for**:
- Reasoning tokens (when `reasoning_effort` > "none") are billed as output tokens
- These are invisible but count toward your costs

**Recommendation**: Start with `reasoning_effort="none"` or `"low"` and increase only if needed.

### Is GPT-5.1 faster or slower?

It depends on `reasoning_effort`:

| Setting | Latency vs GPT-4o |
|---------|-------------------|
| `"none"` | Similar or faster |
| `"low"` | Similar |
| `"medium"` | Slower (more thinking) |
| `"high"` | Significantly slower |

For latency-sensitive applications, use `"none"` or `"low"`.

### How do I optimize costs?

1. Use `reasoning_effort="none"` for simple tasks
2. Leverage prompt caching (90% discount on cached tokens)
3. Monitor token usage closely during migration
4. Right-size `max_completion_tokens` for your needs

---

## Language & Regional

### Does GPT-5.1 handle Arabic well?

Yes, but test thoroughly:
- Model behavior can shift between versions
- Code-switching (Arabic/English mix) needs testing
- Regional dialects may behave differently

**Recommendation**: Dedicate 30%+ of your golden dataset to Arabic test cases.

### Is GPT-5.1 available in my region?

Check the [Azure OpenAI regional availability](https://learn.microsoft.com/azure/ai-foundry/foundry-models/concepts/models-sold-directly-by-azure) page for current deployment options.

For data residency requirements, confirm your deployment type:
- **Regional**: Data stays in region
- **Global**: Data may be processed globally

---

## Getting Help

### Where can I get support?

1. **This repository**: Open an issue for migration questions
2. **Microsoft Support**: Contact your Customer Success team
3. **Azure Documentation**: [Azure OpenAI Docs](https://learn.microsoft.com/azure/ai-foundry/openai/)
4. **Community**: [Microsoft Q&A](https://learn.microsoft.com/answers/)

### My question isn't answered here

Please open an issue in this repository with:
- Your question
- Relevant context (deployment type, use case)
- What you've already tried

We'll add common questions to this FAQ.

---

## Quick Reference

### Parameter Mapping Cheat Sheet

| GPT-4o | GPT-5.1 | Notes |
|--------|---------|-------|
| `temperature` | *(remove)* | Use `reasoning_effort` |
| `top_p` | *(remove)* | |
| `frequency_penalty` | *(remove)* | |
| `presence_penalty` | *(remove)* | |
| `max_tokens` | `max_completion_tokens` | Includes reasoning tokens |
| `role: "system"` | `role: "developer"` | Both work, developer preferred |
| *(new)* | `reasoning_effort` | `"none"`, `"low"`, `"medium"`, `"high"` |

### Key Dates

| Date | Event |
|------|-------|
| March 9, 2026 | Standard deployments auto-upgrade |
| March 31, 2026 | GPT-4o Standard retired |
| October 1, 2026 | GPT-4o PTU retired |

---

*Still have questions? Reach out to your Microsoft Customer Success team!*
