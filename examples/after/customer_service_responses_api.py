"""
Azure OpenAI Responses API Example
==================================

This example shows the NEW Responses API - OpenAI's next-generation API
designed for reasoning models and agentic workflows.

Benefits over Chat Completions:
✅ 3-5% better performance on reasoning tasks
✅ 40-80% better cache utilization (lower costs)
✅ Preserves chain-of-thought across turns
✅ Built-in tools (web_search, file_search, code_interpreter)
✅ Cleaner API design

When to use Responses API:
- Building agentic workflows with tools
- Multi-turn conversations with reasoning
- Migrating from Assistants API (sunset: Aug 26, 2026)
- New projects

When to stick with Chat Completions:
- Simple request-response patterns
- Minimal code changes needed
- App is working well as-is

Based on: https://platform.openai.com/docs/guides/migrate-to-responses
Azure docs: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/responses
"""

import os
from openai import OpenAI

# Azure OpenAI v1 API - use OpenAI client with Azure base_url
# No api_version needed with v1!
client = OpenAI(
    base_url=f"{os.environ['AZURE_OPENAI_ENDPOINT'].rstrip('/')}/openai/v1/",
    api_key=os.environ["AZURE_OPENAI_API_KEY"]
)


def simple_response(user_input: str) -> str:
    """
    Basic Responses API usage.
    
    Notice the cleaner API:
    - 'instructions' instead of messages array with system role
    - 'input' instead of messages array with user role
    - 'output_text' instead of choices[0].message.content
    """
    response = client.responses.create(
        model="gpt-5.1",
        instructions="You are a helpful customer service agent. Be warm and professional.",
        input=user_input
    )
    
    return response.output_text


def response_with_reasoning(user_input: str, context: str) -> str:
    """
    Using reasoning_effort with Responses API.
    
    The Responses API preserves chain-of-thought (CoT) between turns,
    which is why it performs better than Chat Completions for reasoning tasks.
    """
    response = client.responses.create(
        model="gpt-5.1",
        instructions=f"""You are a customer service specialist handling complex issues.
        
Context: {context}

Analyze the situation carefully and provide a thoughtful response.""",
        input=user_input,
        reasoning={"effort": "medium"}  # Controls reasoning depth
    )
    
    return response.output_text


def multi_turn_conversation():
    """
    Multi-turn conversation with automatic history.
    
    With Chat Completions, you manually manage the messages array.
    With Responses API, just pass previous_response_id!
    """
    # Turn 1
    response1 = client.responses.create(
        model="gpt-5.1",
        instructions="You are a helpful assistant.",
        input="My name is Ahmed and I'm having billing issues."
    )
    print(f"Turn 1: {response1.output_text}")
    
    # Turn 2 - automatically has context from Turn 1
    response2 = client.responses.create(
        model="gpt-5.1",
        input="What's my name and what issue am I having?",
        previous_response_id=response1.id  # Magic! Preserves context + reasoning
    )
    print(f"Turn 2: {response2.output_text}")
    
    return response2


def response_with_web_search(query: str) -> str:
    """
    Built-in web search tool.
    
    Responses API has built-in tools - no need to implement function calling!
    """
    response = client.responses.create(
        model="gpt-5.1",
        instructions="Search the web and provide accurate, current information.",
        input=query,
        tools=[{"type": "web_search"}]
    )
    
    return response.output_text


def response_with_custom_function():
    """
    Custom function calling with Responses API.
    
    Similar to Chat Completions, but with cleaner handling.
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_customer_balance",
                "description": "Get the current balance for a customer account",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone_number": {
                            "type": "string",
                            "description": "Customer phone number"
                        }
                    },
                    "required": ["phone_number"]
                }
            }
        }
    ]
    
    response = client.responses.create(
        model="gpt-5.1",
        instructions="You are a billing assistant. Use tools to look up customer information.",
        input="What's the balance for account 55512345?",
        tools=tools
    )
    
    # Check if model wants to call a function
    for item in response.output:
        if item.type == "function_call":
            print(f"Function to call: {item.name}")
            print(f"Arguments: {item.arguments}")
            # You would call your actual function here
    
    return response


def stateful_conversation():
    """
    Stateful conversations with store=True.
    
    Responses are stored by default, enabling:
    - Conversation continuity
    - Better caching
    - Lower costs
    """
    response = client.responses.create(
        model="gpt-5.1",
        instructions="You are a helpful assistant.",
        input="Remember: my favorite color is blue.",
        store=True  # Default is True - conversations are stored
    )
    
    # Later, you can reference this response
    print(f"Response ID: {response.id}")
    print(f"Can continue with: previous_response_id='{response.id}'")
    
    return response


# Comparison: Chat Completions vs Responses API
def comparison_example():
    """
    Side-by-side comparison of the same task in both APIs.
    """
    
    # ==========================================
    # CHAT COMPLETIONS (Old Way)
    # ==========================================
    from openai import AzureOpenAI
    
    old_client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version="2025-06-01"
    )
    
    # More verbose, manual message management
    chat_response = old_client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {"role": "developer", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ],
        max_completion_tokens=100,
        reasoning_effort="low"
    )
    chat_result = chat_response.choices[0].message.content
    
    # ==========================================
    # RESPONSES API (New Way)
    # ==========================================
    
    # Cleaner, more intuitive
    responses_response = client.responses.create(
        model="gpt-5.1",
        instructions="You are a helpful assistant.",
        input="Hello!",
        reasoning={"effort": "low"}
    )
    responses_result = responses_response.output_text
    
    print("Chat Completions result:", chat_result)
    print("Responses API result:", responses_result)


if __name__ == "__main__":
    print("=" * 60)
    print("Azure OpenAI Responses API Examples")
    print("=" * 60)
    
    print("\n📚 This file demonstrates the Responses API.")
    print("Benefits:")
    print("  ✅ 3-5% better reasoning performance")
    print("  ✅ 40-80% better cache utilization")
    print("  ✅ Cleaner API design")
    print("  ✅ Built-in tools (web_search, code_interpreter)")
    print("  ✅ Automatic conversation history")
    
    print("\n📖 Learn more:")
    print("  - OpenAI: https://platform.openai.com/docs/guides/migrate-to-responses")
    print("  - Azure: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/responses")
    
    print("\n⚠️  Note: Requires valid Azure OpenAI credentials to run")
