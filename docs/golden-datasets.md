# Building Golden Datasets for Migration Testing

A golden dataset is your safety net during migration. It's a curated collection of test cases that represent your real-world usage, allowing you to verify that GPT-5.1 performs as well as (or better than) GPT-4o for your specific use cases.

## Why Golden Datasets Matter

Without a golden dataset, you're flying blind:
- ❌ "It seems to work fine" isn't measurable
- ❌ Edge cases slip through
- ❌ Regressions go unnoticed until users complain

With a golden dataset:
- ✅ Quantifiable quality metrics
- ✅ Reproducible testing
- ✅ Confidence in production deployment
- ✅ Evidence for stakeholder sign-off

---

## Dataset Size Recommendations

| Application Complexity | Minimum Size | Recommended |
|-----------------------|--------------|-------------|
| Simple (single task) | 30 cases | 50 cases |
| Medium (few tasks) | 50 cases | 100 cases |
| Complex (many tasks) | 100 cases | 200+ cases |

**Rule of thumb**: If you'd be worried about a specific scenario failing, include it in your dataset.

---

## Dataset Structure

### Basic Format (JSONL)

Each line is a JSON object with these fields:

```json
{
  "test_id": "BILLING_EN_001",
  "query": "The customer's question or input",
  "context": "Any additional context (customer info, conversation history, etc.)",
  "ground_truth": "The expected/ideal response",
  "category": "billing",
  "language": "en",
  "difficulty": "easy",
  "tags": ["billing", "inquiry", "english"]
}
```

### Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `test_id` | Yes | Unique identifier for tracking |
| `query` | Yes | The user input to test |
| `context` | Recommended | Additional context the model receives |
| `ground_truth` | Yes | Expected/ideal response for comparison |
| `category` | Recommended | Group similar test cases |
| `language` | Recommended | For multilingual applications |
| `difficulty` | Optional | easy/medium/hard |
| `tags` | Optional | Flexible categorization |

---

## Sources for Test Cases

### 1. Production Logs (Best Source)
```python
# Example: Extract diverse samples from production
import random

def sample_production_logs(logs, sample_size=100):
    # Group by category
    by_category = {}
    for log in logs:
        cat = log.get('category', 'unknown')
        by_category.setdefault(cat, []).append(log)
    
    # Sample evenly from each category
    samples = []
    per_category = sample_size // len(by_category)
    for cat, items in by_category.items():
        samples.extend(random.sample(items, min(per_category, len(items))))
    
    return samples
```

> ⚠️ **Important**: Remove or anonymize PII before using production data!

### 2. Subject Matter Experts (SMEs)
Ask your domain experts:
- "What questions do customers ask most?"
- "What are the trickiest scenarios?"
- "What must the AI never get wrong?"

### 3. Historical Support Tickets
Review past customer interactions for:
- Common questions
- Edge cases that caused issues
- Complaints about AI responses

### 4. Synthetic Generation
Use GPT-4o to generate test cases (then validate with humans):

```python
prompt = """Generate 10 realistic customer service questions about 
billing for a telecom company. Include a mix of:
- Simple inquiries
- Complex disputes
- Emotional complaints
- Arabic language questions

Format as JSON with query, expected_intent, and language fields."""
```

---

## Categories to Cover

### By Topic (example for telecom)
- Billing inquiries
- Technical support
- Plan changes
- Roaming questions
- Complaints/escalations
- General inquiries

### By Difficulty
- **Easy**: Clear, simple questions with obvious answers
- **Medium**: Questions requiring some context or reasoning
- **Hard**: Ambiguous, multi-part, or emotionally charged

### By Language
- Primary language (e.g., English)
- Secondary languages (e.g., Arabic)
- Code-switching (mixing languages)

### Edge Cases (Critical!)
- Very short inputs ("help")
- Very long inputs (multiple paragraphs)
- Typos and misspellings
- Ambiguous questions
- Out-of-scope requests
- Potentially sensitive topics

---

## Writing Good Ground Truth Responses

### Do:
- Write realistic, high-quality responses
- Include the key information that must be present
- Match your brand's tone and style
- Be specific enough to evaluate against

### Don't:
- Write perfect responses that are unrealistically polished
- Make them too short (hard to evaluate)
- Include information the model shouldn't know
- Copy-paste from production (may include errors)

### Example:

```json
{
  "test_id": "BILLING_EN_001",
  "query": "Hi, I received my bill and there's a charge of 150 QAR that I don't recognize. My number is 55512345.",
  "context": "{\"customer_name\": \"Ahmed\", \"plan\": \"Shahry 300\", \"account_type\": \"Postpaid\"}",
  "ground_truth": "Hello Ahmed, thank you for reaching out. I understand you have a question about a 150 QAR charge on your bill. Let me look into this for your account ending in 12345. I'll review the charges and explain what this is for. If it's an error, we'll make sure it's corrected right away. Can you tell me approximately when this charge appeared on your bill?",
  "category": "billing",
  "language": "en"
}
```

---

## Template: Telecom Customer Service

Here's a ready-to-use template structure:

```json
// Billing - English - Easy
{"test_id": "BILL_EN_E01", "query": "When is my bill due?", "context": "{\"name\": \"Sara\", \"plan\": \"Shahry 200\"}", "ground_truth": "Hi Sara, your Shahry 200 bill is due on the 1st of each month. Would you like me to check your current balance?", "category": "billing", "language": "en", "difficulty": "easy"}

// Billing - Arabic - Easy  
{"test_id": "BILL_AR_E01", "query": "متى موعد سداد فاتورتي؟", "context": "{\"name\": \"خالد\", \"plan\": \"شهري 200\"}", "ground_truth": "مرحباً خالد، موعد سداد فاتورة شهري 200 هو الأول من كل شهر. هل تريدني أن أتحقق من رصيدك الحالي؟", "category": "billing", "language": "ar", "difficulty": "easy"}

// Technical - English - Medium
{"test_id": "TECH_EN_M01", "query": "My internet has been slow for 2 days. I've already restarted the router twice.", "context": "{\"name\": \"Mohammed\", \"plan\": \"SuperNet 100\"}", "ground_truth": "Hi Mohammed, I'm sorry you're experiencing slow internet on your SuperNet 100 connection. Since you've already tried restarting the router, let me check if there are any network issues in your area. Can you tell me your location so I can investigate further? If needed, we can arrange a technician visit.", "category": "technical", "language": "en", "difficulty": "medium"}

// Complaint - English - Hard
{"test_id": "COMP_EN_H01", "query": "This is unacceptable! I've been a customer for 10 years and my internet has been down for 3 days. I've called 5 times and nobody fixed it. I want compensation!", "context": "{\"name\": \"Hamad\", \"plan\": \"Premium SuperNet 200\", \"account_type\": \"VIP\"}", "ground_truth": "Mr. Hamad, I sincerely apologize for this frustrating experience. As a valued 10-year customer, you deserve much better service. I'm taking personal ownership of your case right now. Let me arrange for our priority technical team to visit today, and I'm also applying a credit to your account for the downtime. Can you confirm your preferred time for the technician visit?", "category": "complaint", "language": "en", "difficulty": "hard"}

// Edge Case - Mixed Language
{"test_id": "EDGE_MIX_01", "query": "Hi, أريد أعرف about my bill. My number is 55567890", "context": "{\"name\": \"Youssef\", \"language_pref\": \"Arabic\"}", "ground_truth": "مرحباً يوسف، بكل سرور سأساعدك بخصوص فاتورتك. دعني أراجع حسابك على الرقم 55567890. هل لديك سؤال محدد عن الفاتورة؟", "category": "billing", "language": "mixed", "difficulty": "medium"}
```

---

## Quality Checklist

Before using your dataset, verify:

- [ ] **Coverage**: All major use cases represented
- [ ] **Balance**: Reasonable distribution across categories
- [ ] **Languages**: All supported languages included
- [ ] **Difficulty**: Mix of easy, medium, and hard cases
- [ ] **Edge cases**: Unusual scenarios covered
- [ ] **Ground truth quality**: Responses reviewed by SMEs
- [ ] **No PII**: Personal data removed or anonymized
- [ ] **Formatting**: Valid JSONL, consistent structure

---

## Maintaining Your Dataset

### Version Control
- Store in Git alongside your code
- Tag versions with model versions tested against
- Document changes in a changelog

### Regular Updates
- Add cases when new issues are discovered
- Remove outdated scenarios
- Refresh with recent production samples quarterly

### Validation
- Periodically review with SMEs
- Check that ground truths still represent ideal responses
- Update for policy or product changes

---

## Example Dataset Download

See the `datasets/templates/` folder for:
- `customer_service_template.jsonl` - 50 example test cases
- `multilingual_template.jsonl` - Arabic/English examples
- `edge_cases_template.jsonl` - Edge case examples

---

## Next Steps

1. Start with 50 test cases from your most common scenarios
2. Add 10-20 edge cases
3. Have SMEs review ground truth responses
4. Run your first evaluation (see [Evaluation Guide](evaluation-guide.md))

---

*Need help building your dataset? Your Microsoft Customer Success team can assist!*
