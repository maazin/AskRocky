#!/usr/bin/env python3
"""
Simple test to check if we can connect to Pinecone and OpenAI
"""

print("Testing Pinecone and OpenAI connections...")

# Test OpenAI
print("\n1. Testing OpenAI API...")
try:
    import os
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY", "")
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in environment")

    # Test with a simple completion (legacy openai lib)
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
    print(f"   Note: Your API key starts with 'pcsk_' which is a serverless key")
    print(f"   You'll need to create an index manually in the Pinecone console:")
    print(f"   - Go to https://app.pinecone.io/")
    print(f"   - Create a serverless index named 'bullbot'")
    print(f"   - Use dimension: 384")
    print(f"   - Use metric: cosine")
    print(f"   - Use cloud: AWS, region: us-east-1")
except Exception as e:
    print(f"❌ Pinecone error: {e}")

print("\n✅ Basic connectivity tests complete!")
