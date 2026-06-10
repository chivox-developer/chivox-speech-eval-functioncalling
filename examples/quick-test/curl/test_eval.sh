#!/bin/bash
# Quick test: Chivox Function Calling speech evaluation
# Usage: API_KEY=sk-xxx bash test_eval.sh

API_KEY="${API_KEY:-sk-your-api-key}"
BASE_URL="${BASE_URL:-https://fc-global.cloud.chivox.com}"

echo "=== 1. List Functions ==="
curl -s "$BASE_URL/v1/functions" \
  -H "Authorization: Bearer $API_KEY" \
  | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
for item in data.get('data', []):
    f = item.get('function', {})
    print(f\"  - {f['name']}: {f.get('description', '')[:60]}\")
"
echo ""

echo "=== 2. Evaluate 'hello' (en_word_eval) ==="
curl -s -X POST "$BASE_URL/v1/call" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "en_word_eval",
    "arguments": {
      "ref_text": "hello",
      "audio_url": "https://dict.youdao.com/dictvoice?audio=hello&type=1"
    }
  }' | python3 -m json.tool 2>/dev/null
echo ""

echo "=== 3. Evaluate sentence (en_sentence_eval) ==="
curl -s -X POST "$BASE_URL/v1/call" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "en_sentence_eval",
    "arguments": {
      "ref_text": "The quick brown fox jumps over the lazy dog",
      "audio_url": "https://dict.youdao.com/dictvoice?audio=The+quick+brown+fox+jumps+over+the+lazy+dog&type=1"
    }
  }' | python3 -m json.tool 2>/dev/null
echo ""

echo "=== Done ==="
