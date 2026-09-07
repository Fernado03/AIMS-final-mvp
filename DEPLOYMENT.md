# AIMS Deployment Guide

Local demo uses Docker Mongo (`docker start aims-mongo`). Atlas is only for production.

Flask serves the frontend from `frontend/` (same origin). There is no separate Vercel/config.js split.

## MongoDB Atlas (production DB)

1. Create a free cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Create a database user.
3. Network Access: add the host IP (or `0.0.0.0/0` if you accept that risk).
4. Connection string → `MONGO_URI` in `.env`.

## Host the app

One process: `python -m backend.app` (port 5000). Put it behind nginx/caddy if you need TLS.

Environment:

- `LLM_API_KEY`
- `LLM_BASE_URL` (default `https://api.hcnsec.cn/v1`)
- `LLM_MODEL` (default `glm-5.3-flash`)
- `MONGO_URI`

Do not commit `.env`.
