# Proxy Server Example

A Python Flask proxy server that keeps your API Key secure on the server side. Includes a web-based UI for testing speech evaluation.

## Architecture

```
Browser/App  →  Proxy Server (:5000)  →  FC Service (fc-global.cloud.chivox.com)
                 ↑ Verify JWT            ↑ Inject API Key
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export CVX_API_KEY=sk-your-api-key
```

### 3. Run

```bash
python proxy_server.py
```

Open http://localhost:5000 in your browser. Login with default credentials: `admin` / `admin123`.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CVX_API_KEY` | Yes | - | API Key for the FC service (`sk-xxx`) |
| `CVX_FC_URL` | No | `https://fc-global.cloud.chivox.com` | FC service URL |
| `PROXY_PORT` | No | `5000` | Proxy listen port |
| `JWT_SECRET` | No | (auto-generated) | JWT signing secret |
| `PROXY_USERS` | No | `admin:admin123` | User list (`user1:pass1,user2:pass2`) |

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/auth/login` | No | Login, returns JWT token |
| `GET` | `/v1/functions` | JWT | List available evaluation functions |
| `POST` | `/v1/call` | JWT | Call an evaluation function |
| `GET` | `/health` | No | Health check |
| `GET` | `/` | No | Web UI |

## Test Users

Default: `admin:admin123`

To add more users:

```bash
export PROXY_USERS=alice:secret123,bob:pass456
```
