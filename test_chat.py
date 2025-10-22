import requests
import json

print("Testing Bull Bot API...")
print()

url = "http://localhost:8000/api/chat"
data = {"prompt": "What is USF?"}

print(f"Sending request to {url}")
print(f"Prompt: {data['prompt']}")
print()
print("Waiting for response (this may take 10-30 seconds for first request)...")
print()

try:
    response = requests.post(url, json=data, timeout=60)
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        print("✅ SUCCESS!")
        print()
        print("Answer:")
        print(result['bot']['result'])
        print()
        print("Sources:")
        for i, (title, source) in enumerate(zip(result['bot']['title'], result['bot']['source'])):
            print(f"{i+1}. {title}")
            print(f"   {source}")
    else:
        print("❌ ERROR:")
        print(response.text)
        
except requests.exceptions.Timeout:
    print("❌ Request timed out after 60 seconds")
except Exception as e:
    print(f"❌ Error: {e}")
