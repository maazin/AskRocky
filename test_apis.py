#!/usr/bin/env python3
"""
Simple test to check if we can connect to Pinecone and OpenAI without hardcoding secrets.
"""

import os

print("Testing Pinecone and OpenAI connections...")

# Test OpenAI
print("\n1. Testing OpenAI API...")
try:
    import openai
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment")
    openai.api_key = api_key

    # Test with a simple completion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say hello"}],
        max_tokens=10
    )
    print("✅ OpenAI API is working!")
    print(f"   Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ OpenAI API error: {e}")

# Test Pinecone - just check if we can import
print("\n2. Checking Pinecone library...")
try:
    import pinecone
    print("✅ Pinecone library imported successfully")
    print("   If you plan to use RAG, ensure PINECONE_API_KEY, PINECONE_ENVIRONMENT, and PINECONE_INDEX are set.")
except Exception as e:
    print(f"❌ Pinecone error: {e}")

print("\n✅ Basic connectivity tests complete!")
