# API Reference / API 接入文档

[English](#1-overview) | [中文](#1-概述)

---

## 1. Overview

The Chivox Speech Evaluation Function Calling API provides an OpenAI-compatible REST interface for speech evaluation. It supports two evaluation modes:

- **One-shot evaluation** — Upload complete audio, receive evaluation result
- **Streaming evaluation** — Push audio in real-time via WebSocket, receive intermediate and final results

**Base URL:** `https://fc-global.cloud.chivox.com`

## 1. 概述

驰声语音评测 Function Calling API 提供 OpenAI 兼容的 REST 接口进行语音评测。支持两种评测模式：

- **一次性评测** — 上传完整音频，返回评测结果
- **流式评测** — 通过 WebSocket 实时推送音频，实时获取中间结果和最终结果

**服务地址：** `https://fc-global.cloud.chivox.com`

---

## 2. Authentication / 认证

### 2.1 B2C Authentication (API Key)

All requests require an API Key in the HTTP header:

所有请求需在 HTTP Header 中携带 API Key：

```
Authorization: Bearer <your_api_key>
```

Get your API Key from the [Chivox API Portal](https://api-portal.cloud.chivox.com) (`sk-xxx` format).

从[驰声 API 门户](https://api-portal.cloud.chivox.com)获取 API Key（`sk-xxx` 格式）。

**Example / 示例：**

```bash
curl https://fc-global.cloud.chivox.com/v1/functions \
  -H "Authorization: Bearer sk-your-api-key"
```

```python
import httpx

headers = {"Authorization": "Bearer sk-your-api-key"}
resp = httpx.get("https://fc-global.cloud.chivox.com/v1/functions", headers=headers)
print(resp.json())
```

```javascript
const resp = await fetch("https://fc-global.cloud.chivox.com/v1/functions", {
  headers: { Authorization: "Bearer sk-your-api-key" },
});
console.log(await resp.json());
```

### 2.2 B2B Authentication (JWT)

For enterprise users with Access Key / Secret Key, generate a JWT token and use it as the Bearer token.

企业用户使用 Access Key / Secret Key 生成 JWT Token，将其作为 Bearer Token 使用。

**JWT Payload:**

```json
{
  "iss": "<your_access_key>",
  "iat": 1700000000,
  "exp": 1700000300
}
```

Sign with HMAC-SHA256 using your Secret Key. Recommended expiration: 5 minutes.

使用 Secret Key 进行 HMAC-SHA256 签名。建议过期时间：5 分钟。

**Authentication Errors / 认证错误：**

| Status Code | Scenario / 场景 |
|-------------|-----------------|
| 401 | Missing Authorization header / 缺少 Authorization 头 |
| 403 | Invalid or disabled API Key / API Key 无效或已禁用 |

---

## 3. API Endpoints / API 端点

| Method | Path | Description / 说明 |
|--------|------|-------------------|
| `GET` | `/v1/functions` | List all available evaluation functions / 列出所有可用评测函数 |
| `POST` | `/v1/call` | Call an evaluation function / 调用评测函数 |
| `WebSocket` | `/ws/eval/{session_id}` | Stream audio for real-time evaluation / 流式音频传输 |

---

## 4. List Functions / 列出函数

**Request / 请求：**

```
GET /v1/functions
Authorization: Bearer <api_key>
```

**Response / 响应：**

```json
{
  "object": "list",
  "data": [
    {
      "type": "function",
      "function": {
        "name": "en_word_eval",
        "description": "English word pronunciation evaluation...",
        "parameters": { "type": "object", "properties": { ... } }
      }
    }
  ]
}
```

---

## 5. Call Function / 调用函数

### 5.1 Request Format / 请求格式

```
POST /v1/call
Content-Type: application/json
Authorization: Bearer <api_key>
```

```json
{
  "name": "function_name",
  "arguments": {
    "ref_text": "reference text",
    "audio_url": "https://example.com/audio.mp3"
  }
}
```

### 5.2 Audio Input / 音频输入

Two methods (choose one) / 两种方式二选一：

| Parameter / 参数 | Description / 说明 |
|-----------------|-------------------|
| `audio_base64` | Base64 encoded audio data / Base64 编码的音频数据 |
| `audio_url` | HTTP URL of audio file / 音频文件的 HTTP URL |

Maximum audio size: 50MB / 音频大小上限 50MB。

### 5.3 Response Format / 响应格式

**Success / 成功：**

```json
{
  "name": "en_word_eval",
  "result": {
    "overall": 85.5,
    "details": { ... }
  }
}
```

**Error / 失败：**

```json
{
  "name": "en_word_eval",
  "error": {
    "message": "error description"
  }
}
```

### 5.4 Example: English Word Evaluation / 示例：英文单词评测

```bash
curl -X POST https://fc-global.cloud.chivox.com/v1/call \
  -H "Authorization: Bearer sk-your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "en_word_eval",
    "arguments": {
      "ref_text": "hello",
      "audio_url": "https://dict.youdao.com/dictvoice?audio=hello&type=1",
      "accent": 3,
      "rank": 100
    }
  }'
```

### 5.5 Example: Chinese Sentence Evaluation / 示例：中文句子评测

```bash
curl -X POST https://fc-global.cloud.chivox.com/v1/call \
  -H "Authorization: Bearer sk-your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "cn_sentence_eval",
    "arguments": {
      "ref_text": "你好世界",
      "audio_url": "https://example.com/audio.mp3",
      "age_group": "adult",
      "rank": 100
    }
  }'
```

---

## 6. Streaming Evaluation / 流式评测

Streaming evaluation consists of two steps: create a session via HTTP, then push audio via WebSocket.

流式评测分两步：通过 HTTP API 创建会话，然后通过 WebSocket 推送音频。

### 6.1 Workflow / 流程概览

```
Step 1: POST /v1/call  →  call start_stream_eval  →  get session_id + ws_url
                                                        │
Step 2: WebSocket connect ws_url                        │
        ├─ Receive {"type":"ready"}                     │
        ├─ Send binary audio frames...                  │
        ├─ Receive {"type":"intermediate","data":{...}} │
        ├─ Send {"type":"stop"}                         │
        └─ Receive {"type":"result","data":{...}}       │
                                                        │
Step 3: POST /v1/call  →  call get_stream_result  →  get final result (optional)
```

### 6.2 Step 1: Create Session / 创建会话

```bash
curl -X POST https://fc-global.cloud.chivox.com/v1/call \
  -H "Authorization: Bearer sk-your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "start_stream_eval",
    "arguments": {
      "core_type": "en.sent.score",
      "ref_text": "Hello world",
      "audio_type": "mp3",
      "sample_rate": 16000
    }
  }'
```

**Response / 响应：**

```json
{
  "name": "start_stream_eval",
  "result": {
    "session_id": "stream-1713340800-a1b2c3",
    "ws_url": "wss://fc-global.cloud.chivox.com/ws/eval/stream-1713340800-a1b2c3",
    "resume_token": "xK9mN2pQ...",
    "status": "created",
    "message": "Session created. Connect to ws_url and send audio binary frames."
  }
}
```

### 6.3 Step 2: WebSocket Audio Streaming / WebSocket 推送音频

Connect to `ws_url` and start sending audio.

连接 `ws_url`，开始推送音频。

**Client → Server / 客户端 → 服务端：**

| Frame Type | Content | Description / 说明 |
|------------|---------|-------------------|
| Binary | Raw audio data | Send directly after receiving "ready" / 收到 ready 后直接发送 |
| Text | `{"type":"stop"}` | Stop recording / 停止录音 |
| Text | `{"type":"ping"}` | Heartbeat / 心跳 |

**Server → Client / 服务端 → 客户端：**

| Frame Type | Content | Description / 说明 |
|------------|---------|-------------------|
| Text | `{"type":"ready","session":"..."}` | Connection ready / 连接就绪 |
| Text | `{"type":"intermediate","data":{...}}` | Real-time intermediate result / 实时中间结果 |
| Text | `{"type":"result","data":{...}}` | Final evaluation result / 最终评测结果 |
| Text | `{"type":"error","code":"...","message":"..."}` | Error / 错误 |
| Text | `{"type":"pong"}` | Heartbeat response / 心跳响应 |
| Text | `{"type":"backpressure","suggested_interval_ms":200}` | Backpressure / 背压提示 |

### 6.4 Step 3: Get Result (Optional) / 获取结果（可选）

If you didn't receive the result via WebSocket, you can also fetch it via API.

如果未通过 WebSocket 收取结果，也可以通过 API 获取：

```bash
curl -X POST https://fc-global.cloud.chivox.com/v1/call \
  -H "Authorization: Bearer sk-your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_stream_result",
    "arguments": {
      "session_id": "stream-1713340800-a1b2c3",
      "auto_stop": true,
      "timeout": 30
    }
  }'
```

| Parameter / 参数 | Type | Default | Description / 说明 |
|-----------------|------|---------|-------------------|
| `session_id` | string | (required) | Session ID / 会话 ID |
| `auto_stop` | bool | true | Auto stop recording and wait / 自动停止录音并等待结果 |
| `timeout` | number | 30 | Timeout in seconds / 等待超时秒数 |

### 6.5 Reconnection / 断线恢复

After unexpected disconnection, the session stays pending for 60 seconds. Reconnect using `resume_token`:

客户端意外断线后，会话在 60 秒内保持挂起状态，可通过 `resume_token` 重连：

```
wss://fc-global.cloud.chivox.com/ws/eval/{session_id}?resume={resume_token}
```

### 6.6 JavaScript Example / JavaScript 示例

```javascript
// Step 1: Create session
const resp = await fetch("https://fc-global.cloud.chivox.com/v1/call", {
  method: "POST",
  headers: {
    Authorization: "Bearer sk-your-api-key",
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    name: "start_stream_eval",
    arguments: {
      core_type: "en.sent.score",
      ref_text: "Hello world",
      audio_type: "mp3",
      sample_rate: 16000,
    },
  }),
});
const { result } = await resp.json();

// Step 2: WebSocket audio streaming
const ws = new WebSocket(result.ws_url);

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  switch (msg.type) {
    case "ready":
      console.log("Connected, start recording");
      startRecording();
      break;
    case "intermediate":
      console.log("Intermediate result:", msg.data);
      break;
    case "result":
      console.log("Final result:", msg.data);
      ws.close();
      break;
    case "error":
      console.error("Error:", msg.code, msg.message);
      break;
  }
};

// Send audio chunks in recording callback
function onAudioChunk(audioData) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(audioData); // Send binary data directly
  }
}

// Stop recording
function stopRecording() {
  ws.send(JSON.stringify({ type: "stop" }));
}
```

### 6.7 Android Example (OkHttp) / Android 示例

```kotlin
// Step 1: Create session (HTTP request omitted, same as above)
val sessionId = "stream-xxx"
val wsUrl = "wss://fc-global.cloud.chivox.com/ws/eval/$sessionId"

// Step 2: WebSocket
val client = OkHttpClient()
val request = Request.Builder().url(wsUrl).build()

client.newWebSocket(request, object : WebSocketListener() {
    override fun onMessage(webSocket: WebSocket, text: String) {
        val msg = JSONObject(text)
        when (msg.getString("type")) {
            "ready" -> startRecording()
            "intermediate" -> updateUI(msg.getJSONObject("data"))
            "result" -> handleFinalResult(msg.getJSONObject("data"))
            "error" -> handleError(msg.getString("code"), msg.getString("message"))
        }
    }
})

// Send audio in recording callback
fun onAudioData(pcmBytes: ByteArray) {
    webSocket.send(ByteString.of(*pcmBytes))
}

// Stop
fun stop() {
    webSocket.send("{\"type\":\"stop\"}")
}
```

---

## 7. Function Reference / 函数参考

### 7.1 English Evaluation Functions (11) / 英文评测函数

| Function / 函数名 | core_type | Description / 说明 |
|-------------------|-----------|-------------------|
| `en_word_eval` | en.word.score | Word pronunciation scoring / 单词发音评测 |
| `en_word_correction` | en.word.pron | Word pronunciation correction / 单词发音纠错 |
| `en_phonics_eval` | en.nsp.score | Phonics evaluation / 自然拼读评测 |
| `en_sentence_eval` | en.sent.score | Sentence reading assessment / 句子朗读评测 |
| `en_sentence_correction` | en.sent.pron | Sentence pronunciation correction / 句子发音纠错 |
| `en_vocab_eval` | en.vocabs.pron | Multi-word evaluation / 词汇批量评测 |
| `en_paragraph_eval` | en.pred.score | Paragraph reading assessment / 段落朗读评测 |
| `en_realtime_eval` | en.rltm.score | Real-time evaluation / 实时评测 |
| `en_choice_eval` | en.choc.score | Oral choice evaluation / 选择题口语评测 |
| `en_semi_open_eval` | en.scne.exam | Semi-open question / 半开放题 |
| `en_open_eval` | en.prtl.exam | Open question evaluation / 开放题口语评测 |

**Common English Parameters / 英文通用参数：**

| Parameter / 参数 | Type | Required | Default | Description / 说明 |
|-----------------|------|----------|---------|-------------------|
| `ref_text` | string | Yes / 是 | - | Reference text / 参考文本 |
| `audio_base64` | string | One of two / 二选一 | - | Base64 encoded audio / Base64 编码音频 |
| `audio_url` | string | One of two / 二选一 | - | Audio file URL / 音频文件 URL |
| `accent` | number | No / 否 | 3 | 1=British, 2=American, 3=Any / 1=英式, 2=美式, 3=不区分 |
| `rank` | number | No / 否 | 100 | Score scale: 4 or 100 / 评分制: 4 或 100 |
| `attachAudioUrl` | number | No / 否 | 0 | Return audio URL: 0=no, 1=yes / 是否返回音频 URL |

### 7.2 Chinese Evaluation Functions (6) / 中文评测函数

| Function / 函数名 | core_type | Description / 说明 |
|-------------------|-----------|-------------------|
| `cn_word_pinyin_eval` | cn.word.score | Pinyin pronunciation scoring / 拼音/汉字发音评测 |
| `cn_word_raw_eval` | cn.word.raw | Character pronunciation scoring / 汉字发音评测 |
| `cn_sentence_eval` | cn.sent.raw | Sentence reading assessment / 句子朗读评测 |
| `cn_paragraph_eval` | cn.pred.raw | Paragraph reading assessment / 段落朗读评测 |
| `cn_rec_eval` | cn.rec.raw | Limited-branch recognition / 有限分支识别 |
| `cn_aitalk_eval` | cn.recscore.raw | AI Talk — oral expression evaluation / 口语表达评测 |

**Common Chinese Parameters / 中文通用参数：**

| Parameter / 参数 | Type | Required | Default | Description / 说明 |
|-----------------|------|----------|---------|-------------------|
| `ref_text` | string | Yes / 是 | - | Reference text / 参考文本 |
| `audio_base64` | string | One of two / 二选一 | - | Base64 encoded audio / Base64 编码音频 |
| `audio_url` | string | One of two / 二选一 | - | Audio file URL / 音频文件 URL |
| `rank` | number | No / 否 | 100 | Score scale: 4 or 100 / 评分制: 4 或 100 |
| `age_group` | string | No / 否 | "adult" | "child" or "adult" / 儿童或成人 |
| `attachAudioUrl` | number | No / 否 | 0 | Return audio URL: 0=no, 1=yes / 是否返回音频 URL |

### 7.3 Streaming Functions (2) / 流式评测函数

| Function / 函数名 | Description / 说明 |
|-------------------|-------------------|
| `start_stream_eval` | Create streaming session / 创建流式评测会话 |
| `get_stream_result` | Get evaluation result (with auto-stop) / 获取评测结果（可自动停止） |

**start_stream_eval Parameters / 参数：**

| Parameter / 参数 | Type | Required | Default | Description / 说明 |
|-----------------|------|----------|---------|-------------------|
| `core_type` | string | Yes / 是 | - | Evaluation type (see tables above) / 评测类型 |
| `ref_text` | string | Yes / 是 | - | Reference text / 参考文本 |
| `audio_type` | string | No / 否 | "mp3" | Audio format: mp3, wav, pcm |
| `sample_rate` | number | No / 否 | 16000 | Sample rate (Hz) / 采样率 |
| `channel` | number | No / 否 | 1 | Channels: 1=mono, 2=stereo / 声道 |
| `sample_bytes` | number | No / 否 | 2 | Sample bytes: 2=16bit / 采样字节数 |
| `accent` | number | No / 否 | 3 | English accent type (English only) / 英文发音类型 |
| `rank` | number | No / 否 | 100 | Score scale / 评分制 |
| `age_group` | string | No / 否 | "adult" | Age group (Chinese only) / 适用人群 |

---

## 8. Error Handling / 错误处理

### 8.1 HTTP Errors / HTTP 错误

| Status Code | Description / 说明 |
|-------------|-------------------|
| 400 | Bad request / 请求格式错误 |
| 401 | Unauthorized / 未认证 |
| 403 | Forbidden (invalid API Key or no permission) / 权限不足 |
| 404 | Session not found / 会话不存在 |
| 409 | Conflict (invalid session state) / 会话状态不允许当前操作 |

### 8.2 Streaming Error Codes / 流式评测错误码

WebSocket and API return unified error codes:

WebSocket 和 API 返回统一的错误码：

| Error Code | Description / 说明 |
|------------|-------------------|
| SESSION_NOT_FOUND | Session not found / 会话不存在 |
| SESSION_EXPIRED | Session expired / 会话已过期 |
| INVALID_STATE | Invalid state for operation / 当前状态不允许该操作 |
| UPSTREAM_CONNECT | Engine connection failed / 评测引擎连接失败 |
| UPSTREAM_TIMEOUT | Evaluation timeout / 评测超时 |
| UPSTREAM_EVAL_ERROR | Engine returned error / 评测引擎返回错误 |
| CAPACITY_FULL | Concurrent session limit reached / 并发会话已满 |
| AUDIO_TOO_LARGE | Audio exceeds 50MB limit / 音频数据超过 50MB 上限 |
| INVALID_PARAMS | Invalid parameters / 参数无效 |
| RESUME_INVALID | Invalid or expired resume token / 恢复 token 无效或已过期 |

---

## 9. Audio Requirements / 音频要求

| Item / 项目 | Requirement / 要求 |
|-------------|-------------------|
| Format / 格式 | MP3, WAV |
| Sample rate / 采样率 | 16000 Hz (recommended / 推荐) |
| Channels / 声道 | Mono (recommended / 推荐) |
| Bit depth / 位深 | 16bit |
| Max size / 大小上限 | 50MB |

Streaming evaluation recommends MP3 format / 流式评测推荐使用 MP3 格式。

---

## 10. Notes / 注意事项

1. **Audio input / 音频输入：** `audio_base64` and `audio_url` — choose one, both cannot be empty / 二选一，不能同时为空
2. **Streaming timeout / 流式评测超时：** Session expires if no audio received within 60 seconds / 会话创建后 60 秒内无音频输入会自动过期
3. **Reconnection / 断线恢复：** Reconnect within 60 seconds using `resume_token` / 断线后 60 秒内可通过 resume_token 重连
4. **Concurrency limit / 并发限制：** Streaming has a maximum concurrent session limit / 流式评测有最大并发会话数限制
5. **Function permissions / 评测类型权限：** API Key may be restricted to specific core_types / API Key 可能被限制只能使用特定的评测类型
