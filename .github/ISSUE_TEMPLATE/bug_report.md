---
name: Bug Report
about: Report an issue with the Chivox Function Calling service
title: '[Bug] '
labels: bug
---

## Description

A clear description of the issue.

## Environment

- **Client:** (e.g., Python, Node.js, curl, custom app)
- **Auth type:** B2C (API Key) / B2B (JWT)
- **API Key prefix:** (e.g., `sk-a1b2...`, do NOT include the full key)

## Steps to Reproduce

1. ...
2. ...

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened.

## Request / Response

```bash
# Request
curl -X POST https://fc-global.cloud.chivox.com/v1/call \
  -H "Authorization: Bearer sk-..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "...",
    "arguments": { ... }
  }'
```

```json
// Response or error
{ ... }
```

## Additional Context

Any other relevant information (audio format, file size, etc.)
