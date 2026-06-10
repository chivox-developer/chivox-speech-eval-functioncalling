/**
 * Quick test: Chivox Function Calling speech evaluation
 * Usage: node test_eval.js
 *
 * No external dependencies required (uses built-in fetch).
 */

const API_KEY = "sk-your-api-key";
const BASE_URL = "https://fc-global.cloud.chivox.com";

const HEADERS = {
  Authorization: `Bearer ${API_KEY}`,
  "Content-Type": "application/json",
};

async function main() {
  // 1. List functions
  console.log("=== List Functions ===");
  let resp = await fetch(`${BASE_URL}/v1/functions`, { headers: HEADERS });
  let data = await resp.json();
  const functions = data?.data || [];
  functions.forEach((item) => {
    const f = item.function || {};
    console.log(`  - ${f.name}: ${(f.description || "").slice(0, 60)}`);
  });

  // 2. Evaluate word
  console.log("\n=== Evaluate 'hello' (en_word_eval) ===");
  resp = await fetch(`${BASE_URL}/v1/call`, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify({
      name: "en_word_eval",
      arguments: {
        ref_text: "hello",
        audio_url: "https://dict.youdao.com/dictvoice?audio=hello&type=1",
      },
    }),
  });
  data = await resp.json();
  console.log(JSON.stringify(data, null, 2));

  // 3. Evaluate sentence
  console.log("\n=== Evaluate sentence (en_sentence_eval) ===");
  resp = await fetch(`${BASE_URL}/v1/call`, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify({
      name: "en_sentence_eval",
      arguments: {
        ref_text: "The quick brown fox jumps over the lazy dog",
        audio_url:
          "https://dict.youdao.com/dictvoice?audio=The+quick+brown+fox+jumps+over+the+lazy+dog&type=1",
      },
    }),
  });
  data = await resp.json();
  console.log(JSON.stringify(data, null, 2));
}

main().catch(console.error);
