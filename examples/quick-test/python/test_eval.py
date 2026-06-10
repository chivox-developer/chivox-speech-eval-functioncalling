"""
Quick test: Chivox Function Calling speech evaluation
Usage: python test_eval.py

Prerequisites: pip install httpx
"""

import json
import httpx

API_KEY = "sk-your-api-key"
BASE_URL = "https://fc-global.cloud.chivox.com"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


# 1. List functions
print("=== List Functions ===")
resp = httpx.get(f"{BASE_URL}/v1/functions", headers=HEADERS, timeout=30)
data = resp.json()
for item in data.get("data", []):
    f = item.get("function", {})
    print(f"  - {f['name']}: {f.get('description', '')[:60]}")

# 2. Evaluate word
print("\n=== Evaluate 'hello' (en_word_eval) ===")
resp = httpx.post(
    f"{BASE_URL}/v1/call",
    headers=HEADERS,
    json={
        "name": "en_word_eval",
        "arguments": {
            "ref_text": "hello",
            "audio_url": "https://dict.youdao.com/dictvoice?audio=hello&type=1",
        },
    },
    timeout=60,
)
print(json.dumps(resp.json(), indent=2, ensure_ascii=False))

# 3. Evaluate sentence
print("\n=== Evaluate sentence (en_sentence_eval) ===")
resp = httpx.post(
    f"{BASE_URL}/v1/call",
    headers=HEADERS,
    json={
        "name": "en_sentence_eval",
        "arguments": {
            "ref_text": "The quick brown fox jumps over the lazy dog",
            "audio_url": "https://dict.youdao.com/dictvoice?audio=The+quick+brown+fox+jumps+over+the+lazy+dog&type=1",
        },
    },
    timeout=60,
)
print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
