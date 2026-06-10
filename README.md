# Chivox Speech Evaluation Function Calling API

**驰声语音评测 Function Calling API**

> Integrate AI-powered speech & pronunciation evaluation into any application via OpenAI-compatible REST API.

[English](#english) | [中文](#中文)

---

## English

### What is this?

Chivox Speech Evaluation Function Calling API exposes professional speech assessment capabilities as an OpenAI-compatible REST API. Call evaluation functions directly from any HTTP client — no special SDK or protocol required.

**Service endpoint:** `https://fc-global.cloud.chivox.com`

### Features

- **17 evaluation functions** — word, sentence, paragraph, phonics, real-time reading, and more
- **English + Chinese** — 11 English functions, 6 Chinese functions
- **Real-time streaming** — WebSocket-based live audio evaluation
- **Multiple audio inputs** — URL, Base64, or file upload
- **OpenAI-compatible** — standard REST API, works with any HTTP client
- **Stateless calls** — no session initialization needed, call functions directly
- **Dual authentication** — B2C (API Key) and B2B (JWT)

### Quick Start

#### 1. Get Your API Key

Sign up at the [Chivox API Portal](https://api-portal.cloud.chivox.com) to obtain your API Key (`sk-xxx` format).

#### 2. List Available Functions

```bash
curl https://fc-global.cloud.chivox.com/v1/functions \
  -H "Authorization: Bearer sk-your-api-key"
```

#### 3. Evaluate Pronunciation

```bash
curl -X POST https://fc-global.cloud.chivox.com/v1/call \
  -H "Authorization: Bearer sk-your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "en_word_eval",
    "arguments": {
      "ref_text": "hello",
      "audio_url": "https://dict.youdao.com/dictvoice?audio=hello&type=1"
    }
  }'
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/functions` | List all available evaluation functions |
| `POST` | `/v1/call` | Call an evaluation function |
| `WebSocket` | `/ws/eval/{session_id}` | Stream audio for real-time evaluation |

### Available Functions

#### English Evaluation

| Function | Description | core_type |
|----------|-------------|-----------|
| `en_word_eval` | Word pronunciation scoring | `en.word.score` |
| `en_word_correction` | Word pronunciation correction | `en.word.pron` |
| `en_phonics_eval` | Phonics evaluation | `en.nsp.score` |
| `en_sentence_eval` | Sentence reading assessment | `en.sent.score` |
| `en_sentence_correction` | Sentence pronunciation correction | `en.sent.pron` |
| `en_vocab_eval` | Multi-word evaluation | `en.vocabs.pron` |
| `en_paragraph_eval` | Paragraph reading assessment | `en.pred.score` |
| `en_realtime_eval` | Real-time reading evaluation | `en.rltm.score` |
| `en_choice_eval` | Oral choice evaluation | `en.choc.score` |
| `en_semi_open_eval` | Semi-open question evaluation | `en.scne.exam` |
| `en_open_eval` | Open question evaluation | `en.prtl.exam` |

#### Chinese Evaluation

| Function | Description | core_type |
|----------|-------------|-----------|
| `cn_word_pinyin_eval` | Pinyin pronunciation scoring | `cn.word.score` |
| `cn_word_raw_eval` | Character pronunciation scoring | `cn.word.raw` |
| `cn_sentence_eval` | Sentence reading assessment | `cn.sent.raw` |
| `cn_paragraph_eval` | Paragraph reading assessment | `cn.pred.raw` |
| `cn_rec_eval` | Limited-branch recognition | `cn.rec.raw` |
| `cn_aitalk_eval` | AI Talk — oral expression evaluation | `cn.recscore.raw` |

#### Streaming Evaluation

| Function | Description |
|----------|-------------|
| `start_stream_eval` | Create a streaming session, returns `session_id` and WebSocket URL |
| `get_stream_result` | Get evaluation result (with optional auto-stop) |

### Streaming Workflow

```
1. Create session    →  POST /v1/call (start_stream_eval)
                         ↓ returns ws_url
2. Connect WebSocket →  wss://fc-global.cloud.chivox.com/ws/eval/{session_id}
                         ↓
3. Send audio frames →  Binary frames (send directly after "ready" message)
                         ↓
4. Stop & get result →  Send {"type": "stop"}, receive final scores
```

### Examples

| Example | Description |
|---------|-------------|
| [Proxy Server](examples/proxy-server/) | Python Flask proxy server with web UI (keeps API Key server-side) |
| [Quick Test Scripts](examples/quick-test/) | Minimal test scripts in Python, Node.js, and curl |

### Documentation

- [API Reference](docs/api-reference.md) — Full API documentation, authentication, function parameters, and streaming details

### Support

- Website: [chivox.com](https://www.chivox.com)
- Issues: [GitHub Issues](https://github.com/chivox-developer/chivox-speech-eval-functioncalling/issues)

---

## 中文

### 简介

驰声语音评测 Function Calling API 提供 OpenAI 兼容的 REST API，将专业语音评测能力封装为可直接调用的函数。无需特殊 SDK，任何 HTTP 客户端都可以使用。

**服务地址：** `https://fc-global.cloud.chivox.com`

### 功能特性

- **17 种评测函数** — 单词、句子、段落、自然拼读、实时朗读等
- **中英文双语** — 11 种英文评测 + 6 种中文评测
- **实时流式评测** — 通过 WebSocket 实时推送音频，获取评测结果
- **多种音频输入** — 支持 URL、Base64 编码、文件上传
- **OpenAI 兼容** — 标准 REST API，任何 HTTP 客户端均可使用
- **无状态调用** — 无需初始化会话，直接调用函数
- **双认证模式** — B2C（API Key）和 B2B（JWT 签名）

### 快速开始

#### 1. 获取 API Key

访问[驰声 API 门户](https://api-portal.cloud.chivox.com)注册并获取 API Key（`sk-xxx` 格式）。

#### 2. 列出可用函数

```bash
curl https://fc-global.cloud.chivox.com/v1/functions \
  -H "Authorization: Bearer sk-your-api-key"
```

#### 3. 调用评测

```bash
curl -X POST https://fc-global.cloud.chivox.com/v1/call \
  -H "Authorization: Bearer sk-your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "en_word_eval",
    "arguments": {
      "ref_text": "hello",
      "audio_url": "https://dict.youdao.com/dictvoice?audio=hello&type=1"
    }
  }'
```

### API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/v1/functions` | 列出所有可用评测函数 |
| `POST` | `/v1/call` | 调用评测函数 |
| `WebSocket` | `/ws/eval/{session_id}` | 流式音频传输 |

### 评测函数列表

#### 英文评测

| 函数名 | 说明 | core_type |
|--------|------|-----------|
| `en_word_eval` | 单词评测 — 总分及每个音标得分 | `en.word.score` |
| `en_word_correction` | 单词纠音 — 发音纠正建议 | `en.word.pron` |
| `en_phonics_eval` | 自然拼读评测 | `en.nsp.score` |
| `en_sentence_eval` | 句子评测 — 流利度、准确度、完整度 | `en.sent.score` |
| `en_sentence_correction` | 句子纠音 | `en.sent.pron` |
| `en_vocab_eval` | 词语评测 | `en.vocabs.pron` |
| `en_paragraph_eval` | 段落评测 — 每句、每词得分 | `en.pred.score` |
| `en_realtime_eval` | 实时朗读评测 | `en.rltm.score` |
| `en_choice_eval` | 口语选择题评测 | `en.choc.score` |
| `en_semi_open_eval` | 半开放题评测 | `en.scne.exam` |
| `en_open_eval` | 开放题口语评测 | `en.prtl.exam` |

#### 中文评测

| 函数名 | 说明 | core_type |
|--------|------|-----------|
| `cn_word_pinyin_eval` | 拼音评测 — 总分、声母、韵母、声调 | `cn.word.score` |
| `cn_word_raw_eval` | 汉字评测 | `cn.word.raw` |
| `cn_sentence_eval` | 词句评测 — 总分、声调、准确度、流利度 | `cn.sent.raw` |
| `cn_paragraph_eval` | 段落评测 | `cn.pred.raw` |
| `cn_rec_eval` | 有限分支识别 | `cn.rec.raw` |
| `cn_aitalk_eval` | AI Talk — 识别并评测口语表达 | `cn.recscore.raw` |

#### 流式评测

| 函数名 | 说明 |
|--------|------|
| `start_stream_eval` | 创建流式评测会话，返回 session_id 和 WebSocket 地址 |
| `get_stream_result` | 获取评测结果（可自动停止） |

### 流式评测流程

```
1. 创建会话      →  POST /v1/call (start_stream_eval)
                      ↓ 返回 ws_url
2. 连接 WebSocket →  wss://fc-global.cloud.chivox.com/ws/eval/{session_id}
                      ↓
3. 推送音频帧     →  二进制帧（收到 "ready" 消息后直接发送）
                      ↓
4. 停止并获取结果 →  发送 {"type": "stop"}，接收最终评分
```

### 示例

| 示例 | 说明 |
|------|------|
| [代理服务器](examples/proxy-server/) | Python Flask 代理服务 + Web UI，API Key 安全中转 |
| [快速测试脚本](examples/quick-test/) | Python、Node.js、curl 最小化调用示例 |

### 文档

- [API 接入文档](docs/api-reference.md) — 完整 API 文档、认证方式、函数参数、流式评测说明

### 支持

- 官网：[chivox.com](https://www.chivox.com)
- 问题反馈：[GitHub Issues](https://github.com/chivox-developer/chivox-speech-eval-functioncalling/issues)

---

## License

The example code and documentation in this repository are licensed under the [MIT License](LICENSE).

The Chivox Speech Evaluation Function Calling Service is a commercial product. Visit the [Chivox API Portal](https://api-portal.cloud.chivox.com) for service access and pricing.
