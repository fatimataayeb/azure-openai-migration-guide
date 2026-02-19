"""
Azure OpenAI GPT-5.1 Example - AFTER Migration
==============================================

This is the MIGRATED code ready for GPT-5.1.

Changes made:
✅ Updated API version to 2025-06-01
✅ Changed model to gpt-5.1
✅ Removed temperature, top_p, frequency_penalty
✅ Renamed max_tokens to max_completion_tokens
✅ Changed 'system' role to 'developer'
✅ Added reasoning_effort parameter
"""

import os
from openai import AzureOpenAI

# Initialize client with NEW API version
client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version="2025-06-01"  # ✅ Updated
)

def classify_intent(customer_message: str) -> dict:
    """Classify customer intent from their message."""
    
    response = client.chat.completions.create(
        model="gpt-5.1",  # ✅ Updated
        messages=[
            {
                "role": "developer",  # ✅ Changed from "system"
                "content": """Classify the customer message into one of these intents:
                - BILLING: Questions about bills, payments, charges
                - TECHNICAL: Network issues, connectivity problems
                - PLAN_CHANGE: Upgrade, downgrade, modify plans
                - COMPLAINT: Service complaints, escalations
                - GENERAL: General inquiries
                
                Respond with JSON: {"intent": "CATEGORY", "confidence": 0.0-1.0}"""
            },
            {
                "role": "user",
                "content": customer_message
            }
        ],
        # ✅ Removed: temperature, top_p
        max_completion_tokens=100,  # ✅ Renamed from max_tokens
        reasoning_effort="none",    # ✅ Added: fast mode for simple classification
        response_format={"type": "json_object"}
    )
    
    return response.choices[0].message.content


def generate_response(customer_message: str, intent: str, customer_name: str) -> str:
    """Generate a helpful response to the customer."""
    
    response = client.chat.completions.create(
        model="gpt-5.1",  # ✅ Updated
        messages=[
            {
                "role": "developer",  # ✅ Changed from "system"
                "content": f"""You are a friendly, warm, and professional customer service agent.

Customer Name: {customer_name}
Detected Intent: {intent}

Personality:
- Warm and welcoming
- Use the customer's name
- Show empathy before offering solutions
- If the customer writes in Arabic, respond in Arabic"""
            },
            {
                "role": "user",
                "content": customer_message
            }
        ],
        # ✅ Removed: temperature, frequency_penalty
        max_completion_tokens=500,  # ✅ Renamed from max_tokens
        reasoning_effort="low",     # ✅ Added: thoughtful responses
    )
    
    return response.choices[0].message.content


def generate_complex_response(customer_message: str, customer_context: dict) -> str:
    """
    Handle complex complaints requiring deeper analysis.
    
    Uses higher reasoning_effort for thorough responses.
    """
    
    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {
                "role": "developer",
                "content": f"""You are a senior customer service specialist handling escalated cases.

Customer: {customer_context.get('name', 'Valued Customer')}
Account Type: {customer_context.get('account_type', 'Standard')}
Tenure: {customer_context.get('tenure', 'Unknown')}

For this complaint:
1. Acknowledge the customer's frustration empathetically
2. Take ownership of the issue
3. Explain what you'll do to resolve it
4. Offer appropriate compensation if warranted
5. Provide a clear timeline for resolution"""
            },
            {
                "role": "user",
                "content": customer_message
            }
        ],
        max_completion_tokens=800,
        reasoning_effort="medium",  # ✅ Higher reasoning for complex cases
    )
    
    return response.choices[0].message.content


def extract_entities(customer_message: str) -> dict:
    """Extract key entities like phone numbers, dates, amounts."""
    
    response = client.chat.completions.create(
        model="gpt-5.1",  # ✅ Updated
        messages=[
            {
                "role": "developer",  # ✅ Changed from "system"
                "content": """Extract entities from the customer message.
                
Return JSON with these fields (use null if not found):
{
    "phone_numbers": ["list of phone numbers"],
    "dates": ["list of dates mentioned"],
    "amounts": ["list of monetary amounts"],
    "plan_names": ["list of plan names"]
}"""
            },
            {
                "role": "user",
                "content": customer_message
            }
        ],
        # ✅ Removed: temperature
        max_completion_tokens=200,  # ✅ Renamed from max_tokens
        reasoning_effort="none",    # ✅ Added: fast extraction
        response_format={"type": "json_object"}
    )
    
    return response.choices[0].message.content


# Example usage
if __name__ == "__main__":
    test_message = "Hi, my bill shows a charge of 150 QAR I don't recognize. My number is 55512345."
    
    print("=" * 60)
    print("GPT-5.1 Example - AFTER Migration")
    print("=" * 60)
    print(f"\nCustomer message: {test_message}")
    
    print("\n✅ This code is ready for GPT-5.1:")
    print("   - API version: 2025-06-01")
    print("   - Model: gpt-5.1")
    print("   - Role: developer")
    print("   - Parameter: max_completion_tokens")
    print("   - Parameter: reasoning_effort")
    print("\n✅ Removed unsupported parameters:")
    print("   - temperature")
    print("   - top_p")
    print("   - frequency_penalty")
