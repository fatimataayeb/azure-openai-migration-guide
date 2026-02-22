# Azure OpenAI GPT-4o to GPT-5.1 Migration Guide

> 
> **Your smooth path to the next generation of AI** 🚀

Welcome! This guide helps you seamlessly migrate your Azure OpenAI applications from GPT-4o to GPT-5.1. Microsoft has made significant improvements in GPT-5.1 including better reasoning capabilities, improved accuracy, and more cost-effective pricing — and we're here to help you take full advantage of these enhancements.

## 🎯 What's This About?

Microsoft is upgrading Azure OpenAI to GPT-5.1, bringing you:

- **50% lower input token costs** ($1.25/M vs $2.50/M)
- **~45% fewer hallucinations** with improved factual accuracy
- **New reasoning capabilities** with adjustable depth
- **Better instruction following** for more predictable outputs

This repository provides everything you need for a successful migration with minimal disruption to your services.

## 📁 What's Included

```
├── docs/
│   ├── migration-guide.md      # Step-by-step migration instructions
│   ├── api-changes.md          # Detailed API parameter changes
│   ├── golden-datasets.md      # How to build evaluation datasets
│   ├── evaluation-guide.md     # Azure AI Foundry evaluation setup
│   └── faq.md                  # Frequently asked questions
├── examples/
│   ├── before/                 # GPT-4o code examples
│   ├── after/                  # GPT-5.1 migrated code
│   └── evaluation/             # Evaluation pipeline examples
├── scripts/
│   ├── audit_codebase.py       # Find parameters that need updating
│   └── run_evaluation.py       # Run model comparison evaluations
├── datasets/
│   └── templates/              # Golden dataset templates
└── presentation/
    └── migration_deck.pptx     # Customer presentation deck
```

## ⏰ Key Dates

| Date                      | What Happens                                 | Who's Affected          |
| ------------------------- | -------------------------------------------- | ----------------------- |
| **March 9, 2026**   | Auto-upgrade begins for Standard deployments | Dev/Test environments   |
| **March 31, 2026**  | GPT-4o Standard deployments retired          | Dev/Test environments   |
| **October 1, 2026** | GPT-4o PTU deployments retired               | Production environments |

> 💡 **Good news**: You have plenty of time to test thoroughly before production deadlines!

## 🚀 Quick Start

### 1. Check Your Current Setup

```bash
# Clone this repo
git clone https://github.com/your-org/azure-openai-migration-guide.git
cd azure-openai-migration-guide

# Audit your codebase for parameters that need updating
python scripts/audit_codebase.py --path /path/to/your/code
```

### 2. Update Your Code

The main changes are straightforward:

```python
# Before (GPT-4o)
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "system", "content": "..."}],
    temperature=0.7,
    max_tokens=500
)

# After (GPT-5.1)
response = client.chat.completions.create(
    model="gpt-5.1",
    messages=[{"role": "developer", "content": "..."}],
    max_completion_tokens=500,
    reasoning_effort="low"
)
```

### 3. Test with Evaluations

```bash
# Set up your environment
pip install azure-ai-evaluation openai

# Run comparison evaluation
python scripts/run_evaluation.py --dataset datasets/your_golden_dataset.jsonl
```

## 📖 Documentation

| Guide                                            | Description                                  |
| ------------------------------------------------ | -------------------------------------------- |
| [Migration Guide](docs/migration-guide.md)          | Complete step-by-step migration process      |
| [API Changes](docs/api-changes.md)                  | Detailed parameter changes and code examples |
| [Building Golden Datasets](docs/golden-datasets.md) | How to create effective test datasets        |
| [Evaluation Guide](docs/evaluation-guide.md)        | Setting up Azure AI Foundry evaluations      |
| [FAQ](docs/faq.md)                                  | Common questions and answers                 |

## 🛠️ What Needs to Change

| Change        | Before              | After                     | Why                              |
| ------------- | ------------------- | ------------------------- | -------------------------------- |
| API Version   | `2024-10-21`      | `2025-06-01`            | New features support             |
| Model Name    | `gpt-4o`          | `gpt-5.1`               | New model                        |
| System Role   | `"system"`        | `"developer"`           | Improved clarity                 |
| Max Tokens    | `max_tokens`      | `max_completion_tokens` | Includes reasoning tokens        |
| Temperature   | `temperature=0.7` | *(remove)*              | Use `reasoning_effort` instead |
| New Parameter | *(n/a)*           | `reasoning_effort`      | Controls reasoning depth         |

## 💡 Pro Tips

1. **Start testing now** — Use the March 9 auto-upgrade window to test in dev before touching production
2. **Build a golden dataset** — Create 50+ test cases covering your key scenarios (see [guide](docs/golden-datasets.md))
3. **Include multiple languages** — If you serve Arabic/English customers, test both thoroughly
4. **Get stakeholder buy-in** — Show response comparisons to business teams before production rollout
5. **Use reasoning_effort wisely**:

   - `"none"` — Fast, simple tasks (classification, extraction)
   - `"low"` — Standard responses (most use cases)
   - `"medium"` — Complex analysis (complaints, detailed reports)
   - `"high"` — Critical decisions (use sparingly, higher cost)

## 🤝 Getting Help

- **Microsoft Support**: Your Customer Success team is here to help
- **Documentation**: [Azure OpenAI Docs](https://learn.microsoft.com/azure/ai-foundry/openai/)
- **Issues**: Open an issue in this repo for migration questions

## 📊 Migration Checklist

### Before March 9

- [ ] Inventory all Azure OpenAI deployments
- [ ] Review code for parameters that need updating
- [ ] Build golden dataset with test cases
- [ ] Set up evaluation pipeline

### Testing Phase

- [ ] Update code with new parameters
- [ ] Run evaluations comparing GPT-4o vs GPT-5.1
- [ ] Review results with stakeholders
- [ ] Adjust prompts if needed

### Production Rollout

- [ ] Deploy to production (canary first)
- [ ] Monitor quality metrics
- [ ] Scale to 100%
- [ ] Enable continuous evaluation

---

## License

MIT License - Feel free to adapt this for your organization.

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

*Built with ❤️ to help you succeed with Azure OpenAI*
