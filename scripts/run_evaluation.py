#!/usr/bin/env python3
"""
Azure OpenAI Migration Evaluation Script

Compares GPT-4o and GPT-5.1 responses using Azure AI Foundry evaluations.

Usage:
    python run_evaluation.py --dataset golden_dataset.jsonl

Environment variables required:
    AZURE_OPENAI_ENDPOINT - Your Azure OpenAI endpoint
    AZURE_OPENAI_API_KEY - Your Azure OpenAI API key
"""

import argparse
import json
import os
from datetime import datetime
from typing import Dict, List, Any

try:
    from azure.ai.evaluation import (
        CoherenceEvaluator,
        FluencyEvaluator,
        RelevanceEvaluator,
        GroundednessEvaluator,
        SimilarityEvaluator,
        AzureOpenAIModelConfiguration
    )
    from openai import AzureOpenAI
except ImportError:
    print("Error: Required packages not installed.")
    print("Run: pip install azure-ai-evaluation openai")
    exit(1)


class MigrationEvaluator:
    """Evaluator for comparing GPT-4o and GPT-5.1."""
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        gpt4o_deployment: str = "gpt-4o",
        gpt51_deployment: str = "gpt-5.1",
        judge_deployment: str = "gpt-4o"
    ):
        self.endpoint = endpoint
        self.api_key = api_key
        
        # GPT-4o client
        self.client_4o = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version="2024-10-21"
        )
        self.gpt4o_deployment = gpt4o_deployment
        
        # GPT-5.1 client
        self.client_51 = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version="2025-06-01"
        )
        self.gpt51_deployment = gpt51_deployment
        
        # Judge model config
        judge_config = AzureOpenAIModelConfiguration(
            azure_endpoint=endpoint,
            api_key=api_key,
            azure_deployment=judge_deployment,
            api_version="2024-10-21"
        )
        
        # Initialize evaluators
        self.evaluators = {
            "coherence": CoherenceEvaluator(model_config=judge_config),
            "fluency": FluencyEvaluator(model_config=judge_config),
            "relevance": RelevanceEvaluator(model_config=judge_config),
            "groundedness": GroundednessEvaluator(model_config=judge_config),
            "similarity": SimilarityEvaluator(model_config=judge_config)
        }
    
    def generate_response_4o(self, query: str, context: str = "") -> str:
        """Generate response using GPT-4o."""
        messages = [
            {"role": "system", "content": f"You are a helpful assistant. Context: {context}"},
            {"role": "user", "content": query}
        ]
        
        response = self.client_4o.chat.completions.create(
            model=self.gpt4o_deployment,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    
    def generate_response_51(self, query: str, context: str = "") -> str:
        """Generate response using GPT-5.1."""
        messages = [
            {"role": "developer", "content": f"You are a helpful assistant. Context: {context}"},
            {"role": "user", "content": query}
        ]
        
        response = self.client_51.chat.completions.create(
            model=self.gpt51_deployment,
            messages=messages,
            max_completion_tokens=500,
            reasoning_effort="low"
        )
        return response.choices[0].message.content
    
    def evaluate_response(
        self,
        query: str,
        response: str,
        context: str = "",
        ground_truth: str = ""
    ) -> Dict[str, float]:
        """Evaluate a single response."""
        scores = {}
        
        for metric, evaluator in self.evaluators.items():
            try:
                if metric in ["coherence", "fluency"]:
                    result = evaluator(query=query, response=response)
                elif metric == "similarity":
                    if ground_truth:
                        result = evaluator(
                            query=query,
                            response=response,
                            ground_truth=ground_truth
                        )
                    else:
                        continue
                else:
                    result = evaluator(
                        query=query,
                        response=response,
                        context=context or "No additional context provided."
                    )
                
                score = result.get("score", result.get(metric, 0))
                scores[metric] = float(score) if score else 0.0
                
            except Exception as e:
                print(f"Warning: {metric} evaluation failed: {e}")
                scores[metric] = 0.0
        
        return scores
    
    def run_comparison(
        self,
        dataset_path: str,
        output_path: str = None
    ) -> Dict[str, Any]:
        """Run full comparison between GPT-4o and GPT-5.1."""
        
        # Load dataset
        test_cases = []
        with open(dataset_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    test_cases.append(json.loads(line))
        
        print(f"Loaded {len(test_cases)} test cases")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "dataset": dataset_path,
            "test_cases": [],
            "summary": {
                "gpt4o": {},
                "gpt51": {},
                "regressions": []
            }
        }
        
        gpt4o_scores = {m: [] for m in self.evaluators}
        gpt51_scores = {m: [] for m in self.evaluators}
        
        for i, tc in enumerate(test_cases):
            print(f"\nProcessing {i+1}/{len(test_cases)}: {tc.get('test_id', i)}")
            
            query = tc.get("query", "")
            context = tc.get("context", "")
            ground_truth = tc.get("ground_truth", tc.get("expected_output", ""))
            
            # Generate responses
            print("  Generating GPT-4o response...")
            try:
                response_4o = self.generate_response_4o(query, context)
            except Exception as e:
                print(f"  Warning: GPT-4o generation failed: {e}")
                response_4o = ""
            
            print("  Generating GPT-5.1 response...")
            try:
                response_51 = self.generate_response_51(query, context)
            except Exception as e:
                print(f"  Warning: GPT-5.1 generation failed: {e}")
                response_51 = ""
            
            # Evaluate responses
            print("  Evaluating responses...")
            scores_4o = self.evaluate_response(query, response_4o, context, ground_truth)
            scores_51 = self.evaluate_response(query, response_51, context, ground_truth)
            
            # Record results
            test_result = {
                "test_id": tc.get("test_id", f"test_{i}"),
                "query": query,
                "gpt4o": {"response": response_4o, "scores": scores_4o},
                "gpt51": {"response": response_51, "scores": scores_51}
            }
            results["test_cases"].append(test_result)
            
            # Accumulate scores
            for metric in self.evaluators:
                if metric in scores_4o:
                    gpt4o_scores[metric].append(scores_4o[metric])
                if metric in scores_51:
                    gpt51_scores[metric].append(scores_51[metric])
        
        # Calculate summary statistics
        for metric in self.evaluators:
            if gpt4o_scores[metric]:
                results["summary"]["gpt4o"][metric] = {
                    "mean": sum(gpt4o_scores[metric]) / len(gpt4o_scores[metric]),
                    "min": min(gpt4o_scores[metric]),
                    "max": max(gpt4o_scores[metric])
                }
            if gpt51_scores[metric]:
                results["summary"]["gpt51"][metric] = {
                    "mean": sum(gpt51_scores[metric]) / len(gpt51_scores[metric]),
                    "min": min(gpt51_scores[metric]),
                    "max": max(gpt51_scores[metric])
                }
            
            # Check for regressions (>10% drop)
            if gpt4o_scores[metric] and gpt51_scores[metric]:
                mean_4o = results["summary"]["gpt4o"][metric]["mean"]
                mean_51 = results["summary"]["gpt51"][metric]["mean"]
                if mean_4o > 0 and (mean_51 - mean_4o) / mean_4o < -0.1:
                    results["summary"]["regressions"].append({
                        "metric": metric,
                        "gpt4o_mean": mean_4o,
                        "gpt51_mean": mean_51,
                        "drop_percent": round((mean_4o - mean_51) / mean_4o * 100, 2)
                    })
        
        # Save results
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Results saved to {output_path}")
        
        return results
    
    def print_summary(self, results: Dict[str, Any]):
        """Print formatted summary."""
        print("\n" + "=" * 70)
        print("EVALUATION SUMMARY: GPT-4o vs GPT-5.1")
        print("=" * 70)
        
        print("\n📊 AGGREGATE SCORES")
        print("-" * 70)
        print(f"{'Metric':<15} {'GPT-4o Mean':<15} {'GPT-5.1 Mean':<15} {'Difference':<15}")
        print("-" * 70)
        
        for metric in self.evaluators:
            mean_4o = results["summary"]["gpt4o"].get(metric, {}).get("mean", "N/A")
            mean_51 = results["summary"]["gpt51"].get(metric, {}).get("mean", "N/A")
            
            if isinstance(mean_4o, float) and isinstance(mean_51, float):
                diff = mean_51 - mean_4o
                diff_str = f"{diff:+.2f}"
                if diff < -0.3:
                    diff_str += " ⚠️"
                elif diff > 0.1:
                    diff_str += " ✅"
            else:
                diff_str = "N/A"
            
            mean_4o_str = f"{mean_4o:.2f}" if isinstance(mean_4o, float) else str(mean_4o)
            mean_51_str = f"{mean_51:.2f}" if isinstance(mean_51, float) else str(mean_51)
            
            print(f"{metric:<15} {mean_4o_str:<15} {mean_51_str:<15} {diff_str:<15}")
        
        print("-" * 70)
        
        # Regressions
        regressions = results["summary"].get("regressions", [])
        if regressions:
            print("\n⚠️  REGRESSIONS DETECTED (>10% drop)")
            for reg in regressions:
                print(f"   - {reg['metric']}: {reg['drop_percent']:.1f}% drop")
                print(f"     GPT-4o: {reg['gpt4o_mean']:.2f} → GPT-5.1: {reg['gpt51_mean']:.2f}")
        else:
            print("\n✅ NO SIGNIFICANT REGRESSIONS DETECTED")
        
        print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Compare GPT-4o and GPT-5.1 using Azure AI evaluations"
    )
    parser.add_argument(
        "--dataset", "-d",
        required=True,
        help="Path to golden dataset (JSONL format)"
    )
    parser.add_argument(
        "--output", "-o",
        default=f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        help="Output file for results"
    )
    parser.add_argument(
        "--gpt4o-deployment",
        default="gpt-4o",
        help="GPT-4o deployment name"
    )
    parser.add_argument(
        "--gpt51-deployment",
        default="gpt-5.1",
        help="GPT-5.1 deployment name"
    )
    
    args = parser.parse_args()
    
    # Check environment
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    
    if not endpoint or not api_key:
        print("❌ Error: Set environment variables:")
        print("   export AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'")
        print("   export AZURE_OPENAI_API_KEY='your-api-key'")
        return 1
    
    if not os.path.exists(args.dataset):
        print(f"❌ Error: Dataset not found: {args.dataset}")
        return 1
    
    # Run evaluation
    evaluator = MigrationEvaluator(
        endpoint=endpoint,
        api_key=api_key,
        gpt4o_deployment=args.gpt4o_deployment,
        gpt51_deployment=args.gpt51_deployment
    )
    
    results = evaluator.run_comparison(args.dataset, args.output)
    evaluator.print_summary(results)
    
    # Return error code if regressions found
    return 1 if results["summary"]["regressions"] else 0


if __name__ == "__main__":
    exit(main())
