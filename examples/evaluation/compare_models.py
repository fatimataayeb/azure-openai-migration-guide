"""
Model Comparison Example
========================

This script demonstrates how to compare GPT-4o and GPT-5.1 responses
using Azure AI Foundry evaluations.

Usage:
    python compare_models.py

Requirements:
    pip install azure-ai-evaluation openai
"""

import os
import json
from typing import Dict, List

# Check for required packages
try:
    from openai import AzureOpenAI
except ImportError:
    print("Please install: pip install openai")
    exit(1)


def create_clients():
    """Create clients for both GPT-4o and GPT-5.1."""
    
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    
    if not endpoint or not api_key:
        print("❌ Set environment variables:")
        print("   export AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'")
        print("   export AZURE_OPENAI_API_KEY='your-api-key'")
        return None, None
    
    # GPT-4o client (old API)
    client_4o = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2024-10-21"
    )
    
    # GPT-5.1 client (new API)
    client_51 = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2025-06-01"
    )
    
    return client_4o, client_51


def call_gpt4o(client, prompt: str, system_prompt: str = "") -> str:
    """Call GPT-4o with old parameters."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"


def call_gpt51(client, prompt: str, system_prompt: str = "") -> str:
    """Call GPT-5.1 with new parameters."""
    messages = []
    if system_prompt:
        messages.append({"role": "developer", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model="gpt-5.1",
            messages=messages,
            max_completion_tokens=500,
            reasoning_effort="low"
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"


def compare_responses(test_cases: List[Dict]) -> List[Dict]:
    """Compare responses from both models."""
    
    client_4o, client_51 = create_clients()
    if not client_4o:
        return []
    
    results = []
    
    for i, tc in enumerate(test_cases):
        print(f"\nTest {i+1}/{len(test_cases)}: {tc.get('test_id', 'unknown')}")
        
        query = tc.get("query", "")
        system_prompt = tc.get("system_prompt", "You are a helpful assistant.")
        
        # Get responses from both models
        print("  → Calling GPT-4o...")
        response_4o = call_gpt4o(client_4o, query, system_prompt)
        
        print("  → Calling GPT-5.1...")
        response_51 = call_gpt51(client_51, query, system_prompt)
        
        results.append({
            "test_id": tc.get("test_id", f"test_{i}"),
            "query": query,
            "gpt4o_response": response_4o,
            "gpt51_response": response_51,
            "ground_truth": tc.get("ground_truth", "")
        })
        
        # Print comparison
        print(f"\n  GPT-4o: {response_4o[:100]}...")
        print(f"  GPT-5.1: {response_51[:100]}...")
    
    return results


def main():
    """Run comparison on sample test cases."""
    
    # Sample test cases
    test_cases = [
        {
            "test_id": "BILL_EN_001",
            "query": "When is my bill due?",
            "system_prompt": "You are a friendly telecom customer service agent.",
            "ground_truth": "Your bill is due on the 1st of each month."
        },
        {
            "test_id": "TECH_EN_001",
            "query": "My internet is slow. What should I do?",
            "system_prompt": "You are a technical support agent.",
            "ground_truth": "Try restarting your router first."
        },
        {
            "test_id": "COMP_EN_001",
            "query": "I've been overcharged for 3 months! This is unacceptable!",
            "system_prompt": "You are a customer service agent handling complaints.",
            "ground_truth": "I apologize for this. Let me investigate and ensure you receive a refund."
        }
    ]
    
    print("=" * 60)
    print("GPT-4o vs GPT-5.1 Comparison")
    print("=" * 60)
    
    results = compare_responses(test_cases)
    
    if results:
        # Save results
        output_file = "comparison_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Results saved to {output_file}")
        
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)
        print(f"Total tests: {len(results)}")
        print("\nNext steps:")
        print("1. Review the responses manually")
        print("2. Run Azure AI Foundry evaluations for quality metrics")
        print("3. Adjust prompts if GPT-5.1 responses need improvement")
    else:
        print("\n❌ No results generated. Check your credentials.")


if __name__ == "__main__":
    main()
