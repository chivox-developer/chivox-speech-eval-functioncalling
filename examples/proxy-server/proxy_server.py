"""
B2C API Key Proxy Server

Keeps the API Key on the server side. The frontend authenticates via
username/password to obtain a JWT token, then uses the token to access
the proxy. The proxy validates the token and injects the API Key when
forwarding requests to the Function Calling service.

Architecture:
    Browser/App  →  This Proxy (:5000)  →  FC Service
                     ↑ Verify JWT          ↑ Inject API Key

Environment variables:
    CVX_API_KEY   - Required. API Key for the FC service (sk-xxx)
    CVX_FC_URL    - Optional. FC service URL, default https://fc-global.cloud.chivox.com
    PROXY_PORT    - Optional. Proxy listen port, default 5000
    JWT_SECRET    - Optional. JWT signing secret, auto-generated if not set
    PROXY_USERS   - Optional. User list, format: user1:pass1,user2:pass2
                    Default: admin:admin123

Usage:
    export CVX_API_KEY=sk-your-key
    export PROXY_USERS=alice:secret123,bob:pass456
    python proxy_server.py
"""

import os
import sys
import time
import hashlib
import hmac
import json
import base64
import secrets
from functools import wraps

import requests as http_client
from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("CVX_API_KEY", "")
CVX_FC_URL = os.environ.get("CVX_FC_URL", "https://fc-global.cloud.chivox.com").rstrip("/")
JWT_SECRET = os.environ.get("JWT_SECRET", secrets.token_hex(32))
TOKEN_EXPIRE = 24 * 3600  # 24 hours


def _load_users():
    """Load user list from environment variable."""
    raw = os.environ.get("PROXY_USERS", "admin:admin123")
    users = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if ":" in pair:
            username, password = pair.split(":", 1)
            users[username.strip()] = password.strip()
    return users


USERS = _load_users()


# ─── Simple JWT implementation (no third-party dependency) ───


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    s += "=" * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s)


def _sign(payload: str) -> str:
    return _b64url_encode(
        hmac.new(JWT_SECRET.encode(), payload.encode(), hashlib.sha256).digest()
    )


def create_token(username: str) -> str:
    """Generate a JWT token."""
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    claims = _b64url_encode(
        json.dumps(
            {
                "sub": username,
                "iat": int(time.time()),
                "exp": int(time.time()) + TOKEN_EXPIRE,
            }
        ).encode()
    )
    body = f"{header}.{claims}"
    signature = _sign(body)
    return f"{body}.{signature}"


def verify_token(token: str) -> dict | None:
    """Verify JWT token, return claims or None."""
    parts = token.split(".")
    if len(parts) != 3:
        return None

    body = f"{parts[0]}.{parts[1]}"
    if not hmac.compare_digest(_sign(body), parts[2]):
        return None

    try:
        claims = json.loads(_b64url_decode(parts[1]))
    except (json.JSONDecodeError, Exception):
        return None

    if claims.get("exp", 0) < time.time():
        return None

    return claims


# ─── Auth decorator ───


def require_token(f):
    """Verify Bearer token in request."""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Missing Authorization header"}), 401

        token = auth[7:]
        claims = verify_token(token)
        if claims is None:
            return jsonify({"error": "Invalid or expired token"}), 401

        return f(*args, **kwargs)

    return decorated


# ─── Routes ───


@app.route("/auth/login", methods=["POST"])
def login():
    """User login, returns JWT token."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    username = data.get("username", "")
    password = data.get("password", "")

    if username not in USERS or USERS[username] != password:
        return jsonify({"error": "Invalid username or password"}), 401

    token = create_token(username)
    return jsonify({"token": token, "expires_in": TOKEN_EXPIRE})


def forward(method, path):
    """Forward request to FC service, inject API Key."""
    url = f"{CVX_FC_URL}{path}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": request.content_type or "application/json",
    }

    resp = http_client.request(
        method=method,
        url=url,
        headers=headers,
        data=request.get_data(),
        params=request.args,
        timeout=30,
    )

    return Response(
        resp.content,
        status=resp.status_code,
        content_type=resp.headers.get("Content-Type", "application/json"),
    )


@app.route("/v1/call", methods=["POST"])
@require_token
def proxy_call():
    return forward("POST", "/v1/call")


@app.route("/v1/functions", methods=["GET"])
@require_token
def proxy_functions():
    return forward("GET", "/v1/functions")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/", methods=["GET"])
def index():
    return send_from_directory(os.path.dirname(__file__) or ".", "index.html")


if __name__ == "__main__":
    if not API_KEY:
        print("Error: Please set CVX_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    port = int(os.environ.get("PROXY_PORT", "5000"))
    print(f"Proxy server started: http://0.0.0.0:{port}")
    print(f"Forwarding to: {CVX_FC_URL}")
    print(f"API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
    print(f"Loaded {len(USERS)} user(s): {', '.join(USERS.keys())}")
    host = os.environ.get("PROXY_HOST", "127.0.0.1")
    app.run(host=host, port=port)
