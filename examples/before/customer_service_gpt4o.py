"""
Azure OpenAI GPT-4o Example - BEFORE Migration
===============================================

This code will STOP WORKING after March 31, 2026 (Standard) 
or October 1, 2026 (PTU).

Issues that need fixing:
- Uses 'temperature' parameter (removed in GPT-5.1)
- Uses 'top_p' parameter (removed in GPT-5.1)
- Uses 'frequency_penalty' parameter (removed in GPT-5.1)
- Uses 'max_tokens' parameter (renamed to max_completion_tokens)
- Uses 'system' role (deprecated, use 'developer')
- Uses old API version
"""

import os
from openai import AzureOpenAI

# Initialize client with OLD API version
client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version="2024-10-21"  # ❌ Old version
)

def classify_intent(customer_message: str) -> dict:
    """Classify customer intent from their message."""
    
    response = client.chat.completions.create(
        model="gpt-4o",  # ❌ Will be retired
        messages=[
            {
                "role": "system",  # ❌ Deprecated, use "developer"
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
        temperature=0.1,  # ❌ Not supported in GPT-5.1
        top_p=0.95,       # ❌ Not supported in GPT-5.1
        max_tokens=100,   # ❌ Must rename to max_completion_tokens
        response_format={"type": "json_object"}
    )
    
    return response.choices[0].message.content


def generate_response(customer_message: str, intent: str, customer_name: str) -> str:
    """Generate a helpful response to the customer."""
    
    response = client.chat.completions.create(
        model="gpt-4o",  # ❌ Will be retired
        messages=[
            {
                "role": "system",  # ❌ Deprecated
                "content": f"""You are a friendly customer service agent.
                
Customer Name: {customer_name}
Detected Intent: {intent}

Be helpful, warm, and professional. If speaking Arabic, respond in Arabic."""
            },
            {
                "role": "user",
                "content": customer_message
            }
        ],
        temperature=0.7,        # ❌ Not supported in GPT-5.1
        frequency_penalty=0.3,  # ❌ Not supported in GPT-5.1
        max_tokens=500,         # ❌ Must rename to max_completion_tokens
    )
    
    return response.choices[0].message.content


def extract_entities(customer_message: str) -> dict:
    """Extract key entities like phone numbers, dates, amounts."""
    
    response = client.chat.completions.create(
        model="gpt-4o",  # ❌ Will be retired
        messages=[
            {
                "role": "system",  # ❌ Deprecated
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
        temperature=0,    # ❌ Not supported in GPT-5.1
        max_tokens=200,   # ❌ Must rename to max_completion_tokens
        response_format={"type": "json_object"}
    )
    
    return response.choices[0].message.content


# Example usage
if __name__ == "__main__":
    test_message = "Hi, my bill shows a charge of 150 QAR I don't recognize. My number is 55512345."
    
    print("=" * 60)
    print("GPT-4o Example - BEFORE Migration")
    print("=" * 60)
    print(f"\nCustomer message: {test_message}")
    
    # Note: This will fail without valid credentials
    # Demonstrates the code structure that needs to change
    
    print("\n⚠️  This code uses parameters that will cause errors with GPT-5.1:")
    print("   - temperature")
    print("   - top_p") 
    print("   - frequency_penalty")
    print("   - max_tokens (needs renaming)")
    print("   - role: 'system' (deprecated)")
