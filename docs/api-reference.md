# API Reference

[English](#english) | [中文](#中文)

---

## English

### 1. Overview

The Chivox Speech Evaluation Function Calling API provides an OpenAI-compatible REST interface for speech evaluation. It supports two evaluation modes:

- **One-shot evaluation** — Upload complete audio, receive evaluation result
- **Streaming evaluation** — Push audio in real-time via WebSocket, receive intermediate and final results

**Base URL:** `https://fc-global.cloud.chivox.com`

### 2. Authentication

#### 2.1 B2C Authentication (API Key)

All requests require an API Key in the HTTP header:

```
Authorization: Bearer <your_api_key>
```

Get your API Key from the [Chivox API Portal](https://api-portal.cloud.chivox.com) (`sk-xxx` format).

**Examples:**

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

#### 2.2 B2B Authentication (JWT)

For enterprise users with Access Key / Secret Key, generate a JWT token and use it as the Bearer token.

**JWT Payload:**

```json
{
  "iss": "<your_access_key>",
  "iat": 1700000000,
  "exp": 1700000300
}
```

Sign with HMAC-SHA256 using your Secret Key. Recommended expiration: 5 minutes.

**Authentication Errors:**

| Status Code | Scenario |
|-------------|----------|
| 401 | Missing Authorization header |
| 403 | Invalid or disabled API Key |

### 3. API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/functions` | List all available evaluation functions |
| `POST` | `/v1/call` | Call an evaluation function |
| `WebSocket` | `/ws/eval/{session_id}` | Stream audio for real-time evaluation |

### 4. List Functions

**Request:**

```
GET /v1/functions
Authorization: Bearer <api_key>
```

**Response:**

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

### 5. Call Function

#### 5.1 Request Format

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

#### 5.2 Audio Input

Two methods (choose one):

| Parameter | Description |
|-----------|-------------|
| `audio_base64` | Base64 encoded audio data |
| `audio_url` | HTTP URL of audio file |

Maximum audio size: 50MB.

#### 5.3 Response Format

**Success:**

```json
{
  "name": "en_word_eval",
  "result": {
    "overall": 85.5,
    "details": { ... }
  }
}
```

**Error:**

```json
{
  "name": "en_word_eval",
  "error": {
    "message": "error description"
  }
}
```

#### 5.4 Example: English Word Evaluation

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

#### 5.5 Example: Chinese Sentence Evaluation

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

### 6. Streaming Evaluation

Streaming evaluation consists of two steps: create a session via HTTP, then push audio via WebSocket.

#### 6.1 Workflow

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

#### 6.2 Step 1: Create Session

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

**Response:**

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

#### 6.3 Step 2: WebSocket Audio Streaming

Connect to `ws_url` and start sending audio.

**Client → Server:**

| Frame Type | Content | Description |
|------------|---------|-------------|
| Binary | Raw audio data | Send directly after receiving "ready" |
| Text | `{"type":"stop"}` | Stop recording |
| Text | `{"type":"ping"}` | Heartbeat |

**Server → Client:**

| Frame Type | Content | Description |
|------------|---------|-------------|
| Text | `{"type":"ready","session":"..."}` | Connection ready |
| Text | `{"type":"intermediate","data":{...}}` | Real-time intermediate result |
| Text | `{"type":"result","data":{...}}` | Final evaluation result |
| Text | `{"type":"error","code":"...","message":"..."}` | Error |
| Text | `{"type":"pong"}` | Heartbeat response |
| Text | `{"type":"backpressure","suggested_interval_ms":200}` | Backpressure warning |

#### 6.4 Step 3: Get Result (Optional)

If you didn't receive the result via WebSocket, you can also fetch it via API:

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

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session_id` | string | (required) | Session ID |
| `auto_stop` | bool | true | Auto stop recording and wait for result |
| `timeout` | number | 30 | Timeout in seconds |

#### 6.5 Reconnection

After unexpected disconnection, the session stays pending for 60 seconds. Reconnect using `resume_token`:

```
wss://fc-global.cloud.chivox.com/ws/eval/{session_id}?resume={resume_token}
```

#### 6.6 JavaScript Example

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

#### 6.7 Android Example (OkHttp)

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

### 7. Function Reference

#### 7.1 English Evaluation Functions (11)

| Function | core_type | Description |
|----------|-----------|-------------|
| `en_word_eval` | en.word.score | Word pronunciation scoring |
| `en_word_correction` | en.word.pron | Word pronunciation correction |
| `en_phonics_eval` | en.nsp.score | Phonics evaluation |
| `en_sentence_eval` | en.sent.score | Sentence reading assessment |
| `en_sentence_correction` | en.sent.pron | Sentence pronunciation correction |
| `en_vocab_eval` | en.vocabs.pron | Multi-word evaluation |
| `en_paragraph_eval` | en.pred.score | Paragraph reading assessment |
| `en_realtime_eval` | en.rltm.score | Real-time evaluation |
| `en_choice_eval` | en.choc.score | Oral choice evaluation |
| `en_semi_open_eval` | en.scne.exam | Semi-open question |
| `en_open_eval` | en.prtl.exam | Open question evaluation |

**Common English Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ref_text` | string | Yes | - | Reference text |
| `audio_base64` | string | One of two | - | Base64 encoded audio |
| `audio_url` | string | One of two | - | Audio file URL |
| `accent` | number | No | 3 | 1=British, 2=American, 3=Any |
| `rank` | number | No | 100 | Score scale: 4 or 100 |
| `attachAudioUrl` | number | No | 0 | Return audio URL: 0=no, 1=yes |

#### 7.2 Chinese Evaluation Functions (6)

| Function | core_type | Description |
|----------|-----------|-------------|
| `cn_word_pinyin_eval` | cn.word.score | Pinyin pronunciation scoring |
| `cn_word_raw_eval` | cn.word.raw | Character pronunciation scoring |
| `cn_sentence_eval` | cn.sent.raw | Sentence reading assessment |
| `cn_paragraph_eval` | cn.pred.raw | Paragraph reading assessment |
| `cn_rec_eval` | cn.rec.raw | Limited-branch recognition |
| `cn_aitalk_eval` | cn.recscore.raw | AI Talk — oral expression evaluation |

**Common Chinese Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ref_text` | string | Yes | - | Reference text |
| `audio_base64` | string | One of two | - | Base64 encoded audio |
| `audio_url` | string | One of two | - | Audio file URL |
| `rank` | number | No | 100 | Score scale: 4 or 100 |
| `age_group` | string | No | "adult" | "child" or "adult" |
| `attachAudioUrl` | number | No | 0 | Return audio URL: 0=no, 1=yes |

#### 7.3 Streaming Functions (2)

| Function | Description |
|----------|-------------|
| `start_stream_eval` | Create streaming session |
| `get_stream_result` | Get evaluation result (with auto-stop) |

**start_stream_eval Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `core_type` | string | Yes | - | Evaluation type (see tables above) |
| `ref_text` | string | Yes | - | Reference text |
| `audio_type` | string | No | "mp3" | Audio format: mp3, wav, pcm |
| `sample_rate` | number | No | 16000 | Sample rate (Hz) |
| `channel` | number | No | 1 | Channels: 1=mono, 2=stereo |
| `sample_bytes` | number | No | 2 | Sample bytes: 2=16bit |
| `accent` | number | No | 3 | English accent type (English only) |
| `rank` | number | No | 100 | Score scale |
| `age_group` | string | No | "adult" | Age group (Chinese only) |

### 8. Error Handling

#### 8.1 HTTP Errors

| Status Code | Description |
|-------------|-------------|
| 400 | Bad request |
| 401 | Unauthorized |
| 403 | Forbidden (invalid API Key or no permission) |
| 404 | Session not found |
| 409 | Conflict (invalid session state) |

#### 8.2 Streaming Error Codes

WebSocket and API return unified error codes:

| Error Code | Description |
|------------|-------------|
| SESSION_NOT_FOUND | Session not found |
| SESSION_EXPIRED | Session expired |
| INVALID_STATE | Invalid state for operation |
| UPSTREAM_CONNECT | Engine connection failed |
| UPSTREAM_TIMEOUT | Evaluation timeout |
| UPSTREAM_EVAL_ERROR | Engine returned error |
| CAPACITY_FULL | Concurrent session limit reached |
| AUDIO_TOO_LARGE | Audio exceeds 50MB limit |
| INVALID_PARAMS | Invalid parameters |
| RESUME_INVALID | Invalid or expired resume token |

### 9. Audio Requirements

| Item | Requirement |
|------|-------------|
| Format | MP3, WAV |
| Sample rate | 16000 Hz (recommended) |
| Channels | Mono (recommended) |
| Bit depth | 16bit |
| Max size | 50MB |

Streaming evaluation recommends MP3 format.

### 10. Notes

1. **Audio input:** `audio_base64` and `audio_url` — choose one, both cannot be empty
2. **Streaming timeout:** Session expires if no audio received within 60 seconds
3. **Reconnection:** Reconnect within 60 seconds using `resume_token`
4. **Concurrency limit:** Streaming has a maximum concurrent session limit
5. **Function permissions:** API Key may be restricted to specific core_types

---

## 中文

### 1. 概述

驰声语音评测 Function Calling API 提供 OpenAI 兼容的 REST 接口进行语音评测。支持两种评测模式：

- **一次性评测** — 上传完整音频，返回评测结果
- **流式评测** — 通过 WebSocket 实时推送音频，实时获取中间结果和最终结果

**服务地址：** `https://fc-global.cloud.chivox.com`

### 2. 认证

#### 2.1 B2C 认证（API Key）

所有请求需在 HTTP Header 中携带 API Key：

```
Authorization: Bearer <your_api_key>
```

从[驰声 API 门户](https://api-portal.cloud.chivox.com)注册并获取 API Key（`sk-xxx` 格式）。

**示例：**

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

#### 2.2 B2B 认证（JWT 签名）

企业用户使用 Access Key / Secret Key 生成 JWT Token，将其作为 Bearer Token 使用。

**JWT Payload：**

```json
{
  "iss": "<your_access_key>",
  "iat": 1700000000,
  "exp": 1700000300
}
```

使用 Secret Key 进行 HMAC-SHA256 签名。建议过期时间：5 分钟。

**认证错误：**

| 状态码 | 场景 |
|--------|------|
| 401 | 缺少 Authorization 头 |
| 403 | API Key 无效或已禁用 |

### 3. API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/v1/functions` | 列出所有可用评测函数 |
| `POST` | `/v1/call` | 调用评测函数 |
| `WebSocket` | `/ws/eval/{session_id}` | 流式音频传输 |

### 4. 列出函数

**请求：**

```
GET /v1/functions
Authorization: Bearer <api_key>
```

**响应：**

```json
{
  "object": "list",
  "data": [
    {
      "type": "function",
      "function": {
        "name": "en_word_eval",
        "description": "英文单词发音评测...",
        "parameters": { "type": "object", "properties": { ... } }
      }
    }
  ]
}
```

### 5. 调用函数

#### 5.1 请求格式

```
POST /v1/call
Content-Type: application/json
Authorization: Bearer <api_key>
```

```json
{
  "name": "函数名",
  "arguments": {
    "ref_text": "参考文本",
    "audio_url": "https://example.com/audio.mp3"
  }
}
```

#### 5.2 音频输入

两种方式二选一：

| 参数 | 说明 |
|------|------|
| `audio_base64` | Base64 编码的音频数据 |
| `audio_url` | 音频文件的 HTTP URL |

音频大小上限 50MB。

#### 5.3 响应格式

**成功：**

```json
{
  "name": "en_word_eval",
  "result": {
    "overall": 85.5,
    "details": { ... }
  }
}
```

**失败：**

```json
{
  "name": "en_word_eval",
  "error": {
    "message": "错误描述"
  }
}
```

#### 5.4 示例：英文单词评测

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

#### 5.5 示例：中文句子评测

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

### 6. 流式评测

流式评测分两步：通过 HTTP API 创建会话，然后通过 WebSocket 推送音频。

#### 6.1 流程概览

```
步骤1: POST /v1/call  →  调用 start_stream_eval  →  获得 session_id + ws_url
                                                        │
步骤2: WebSocket 连接 ws_url                             │
       ├─ 收到 {"type":"ready"}                          │
       ├─ 发送二进制音频帧...                               │
       ├─ 收到 {"type":"intermediate","data":{...}} (实时) │
       ├─ 发送 {"type":"stop"}                            │
       └─ 收到 {"type":"result","data":{...}}      (最终) │
                                                        │
步骤3: POST /v1/call  →  调用 get_stream_result  →  获取最终结果 (可选)
```

#### 6.2 步骤 1：创建会话

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

**响应：**

```json
{
  "name": "start_stream_eval",
  "result": {
    "session_id": "stream-1713340800-a1b2c3",
    "ws_url": "wss://fc-global.cloud.chivox.com/ws/eval/stream-1713340800-a1b2c3",
    "resume_token": "xK9mN2pQ...",
    "status": "created",
    "message": "会话已创建。通过 WebSocket 连接 ws_url 直接推送音频二进制帧。"
  }
}
```

#### 6.3 步骤 2：WebSocket 推送音频

连接 `ws_url`，开始推送音频。

**客户端 → 服务端：**

| 帧类型 | 内容 | 说明 |
|--------|------|------|
| Binary | 音频原始数据 | 收到 ready 后直接发送 |
| Text | `{"type":"stop"}` | 停止录音 |
| Text | `{"type":"ping"}` | 心跳 |

**服务端 → 客户端：**

| 帧类型 | 内容 | 说明 |
|--------|------|------|
| Text | `{"type":"ready","session":"..."}` | 连接就绪，可以开始发送音频 |
| Text | `{"type":"intermediate","data":{...}}` | 实时中间结果 |
| Text | `{"type":"result","data":{...}}` | 最终评测结果 |
| Text | `{"type":"error","code":"...","message":"..."}` | 错误 |
| Text | `{"type":"pong"}` | 心跳响应 |
| Text | `{"type":"backpressure","suggested_interval_ms":200}` | 背压，请降低发送速度 |

#### 6.4 步骤 3：获取结果（可选）

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

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `session_id` | string | (必填) | 会话 ID |
| `auto_stop` | bool | true | 自动停止录音并等待结果 |
| `timeout` | number | 30 | 等待超时秒数 |

#### 6.5 断线恢复

客户端意外断线后，会话在 60 秒内保持挂起状态，可通过 `resume_token` 重连：

```
wss://fc-global.cloud.chivox.com/ws/eval/{session_id}?resume={resume_token}
```

重连后会收到新的 `ready` 消息，可继续推送音频。每次重连会生成新的 `resume_token`。

#### 6.6 JavaScript 示例

```javascript
// 步骤 1: 创建会话
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

// 步骤 2: WebSocket 推送音频
const ws = new WebSocket(result.ws_url);

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  switch (msg.type) {
    case "ready":
      console.log("连接就绪，开始录音");
      startRecording();
      break;
    case "intermediate":
      console.log("中间结果:", msg.data);
      break;
    case "result":
      console.log("最终结果:", msg.data);
      ws.close();
      break;
    case "error":
      console.error("错误:", msg.code, msg.message);
      break;
  }
};

// 录音回调中发送音频帧
function onAudioChunk(audioData) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(audioData); // 直接发送二进制数据
  }
}

// 录音结束
function stopRecording() {
  ws.send(JSON.stringify({ type: "stop" }));
}
```

#### 6.7 Android 示例 (OkHttp)

```kotlin
// 步骤 1: 创建会话 (省略 HTTP 请求部分，同上)
val sessionId = "stream-xxx"
val wsUrl = "wss://fc-global.cloud.chivox.com/ws/eval/$sessionId"

// 步骤 2: WebSocket
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

// 录音回调中发送音频帧
fun onAudioData(pcmBytes: ByteArray) {
    webSocket.send(ByteString.of(*pcmBytes))
}

// 停止
fun stop() {
    webSocket.send("{\"type\":\"stop\"}")
}
```

### 7. 函数参考

#### 7.1 英文评测函数 (11 个)

| 函数名 | 评测类型 (core_type) | 说明 |
|--------|---------------------|------|
| `en_word_eval` | en.word.score | 单词发音评测 |
| `en_word_correction` | en.word.pron | 单词发音纠错 |
| `en_phonics_eval` | en.nsp.score | 自然拼读评测 |
| `en_sentence_eval` | en.sent.score | 句子朗读评测 |
| `en_sentence_correction` | en.sent.pron | 句子发音纠错 |
| `en_vocab_eval` | en.vocabs.pron | 词汇批量评测 |
| `en_paragraph_eval` | en.pred.score | 段落朗读评测 |
| `en_realtime_eval` | en.rltm.score | 实时评测 |
| `en_choice_eval` | en.choc.score | 选择题口语评测 |
| `en_semi_open_eval` | en.scne.exam | 半开放题（情景对话） |
| `en_open_eval` | en.prtl.exam | 开放题口语评测 |

**英文通用参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `ref_text` | string | 是 | - | 参考文本 |
| `audio_base64` | string | 二选一 | - | Base64 编码音频 |
| `audio_url` | string | 二选一 | - | 音频文件 URL |
| `accent` | number | 否 | 3 | 1=英式, 2=美式, 3=不区分 |
| `rank` | number | 否 | 100 | 评分制: 4 或 100 |
| `attachAudioUrl` | number | 否 | 0 | 是否返回音频 URL: 0=否, 1=是 |

#### 7.2 中文评测函数 (6 个)

| 函数名 | 评测类型 (core_type) | 说明 |
|--------|---------------------|------|
| `cn_word_pinyin_eval` | cn.word.score | 拼音/汉字发音评测 |
| `cn_word_raw_eval` | cn.word.raw | 汉字发音评测 |
| `cn_sentence_eval` | cn.sent.raw | 句子朗读评测 |
| `cn_paragraph_eval` | cn.pred.raw | 段落朗读评测 |
| `cn_rec_eval` | cn.rec.raw | 有限分支识别 |
| `cn_aitalk_eval` | cn.recscore.raw | 口语表达评测 (AI Talk) |

**中文通用参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `ref_text` | string | 是 | - | 参考文本 |
| `audio_base64` | string | 二选一 | - | Base64 编码音频 |
| `audio_url` | string | 二选一 | - | 音频文件 URL |
| `rank` | number | 否 | 100 | 评分制: 4 或 100 |
| `age_group` | string | 否 | "adult" | "child"=儿童, "adult"=成人 |
| `attachAudioUrl` | number | 否 | 0 | 是否返回音频 URL: 0=否, 1=是 |

#### 7.3 流式评测函数 (2 个)

| 函数名 | 说明 |
|--------|------|
| `start_stream_eval` | 创建流式评测会话 |
| `get_stream_result` | 获取评测结果（可自动停止） |

**start_stream_eval 参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `core_type` | string | 是 | - | 评测类型（见上方英文/中文表） |
| `ref_text` | string | 是 | - | 参考文本 |
| `audio_type` | string | 否 | "mp3" | 音频格式: mp3, wav, pcm |
| `sample_rate` | number | 否 | 16000 | 采样率 (Hz) |
| `channel` | number | 否 | 1 | 声道: 1=单声道, 2=立体声 |
| `sample_bytes` | number | 否 | 2 | 采样字节数: 2=16bit |
| `accent` | number | 否 | 3 | 英文发音类型（仅英文） |
| `rank` | number | 否 | 100 | 评分制 |
| `age_group` | string | 否 | "adult" | 适用人群（仅中文） |

### 8. 错误处理

#### 8.1 HTTP 错误

| 状态码 | 说明 |
|--------|------|
| 400 | 请求格式错误 |
| 401 | 未认证 |
| 403 | 权限不足（API Key 无效或无权使用该评测类型） |
| 404 | 会话不存在 |
| 409 | 会话状态不允许当前操作 |

#### 8.2 流式评测错误码

WebSocket 和 API 返回统一的错误码：

| 错误码 | 说明 |
|--------|------|
| SESSION_NOT_FOUND | 会话不存在 |
| SESSION_EXPIRED | 会话已过期 |
| INVALID_STATE | 当前状态不允许该操作 |
| UPSTREAM_CONNECT | 评测引擎连接失败 |
| UPSTREAM_TIMEOUT | 评测超时 |
| UPSTREAM_EVAL_ERROR | 评测引擎返回错误 |
| CAPACITY_FULL | 并发会话已满 |
| AUDIO_TOO_LARGE | 音频数据超过 50MB 上限 |
| INVALID_PARAMS | 参数无效 |
| RESUME_INVALID | 恢复 token 无效或已过期 |

### 9. 音频要求

| 项目 | 要求 |
|------|------|
| 格式 | MP3, WAV |
| 采样率 | 16000 Hz（推荐） |
| 声道 | 单声道（推荐） |
| 位深 | 16bit |
| 大小上限 | 50MB |

流式评测推荐使用 MP3 格式。

### 10. 注意事项

1. **音频输入：** `audio_base64` 和 `audio_url` 二选一，不能同时为空
2. **流式评测超时：** 会话创建后 60 秒内无音频输入会自动过期
3. **断线恢复：** 客户端断线后 60 秒内可通过 `resume_token` 重连
4. **并发限制：** 流式评测有最大并发会话数限制，超限时返回 `CAPACITY_FULL`
5. **评测类型权限：** API Key 可能被限制只能使用特定的评测类型 (core_type)
