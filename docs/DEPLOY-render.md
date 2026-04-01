# 🚀 Render Deployment Guide — Backend Only

> **Stack:** FastAPI + Docker + FAISS  
> **Platform:** Render (Web Service — Docker)  
> **Entry Point:** `backend/main.py`

---

## Pre-Flight Checklist

- [x] `backend/Dockerfile` — present and using Python 3.12-slim
- [x] `render.yaml` — configured with FAISS persistent disk
- [x] `requirements.txt` — all dependencies listed
- [x] `backend/app/` — application code structured
- [x] Git repo clean and pushed to GitHub

---

## Step 1 — Create a Render Account

1. Go to **https://render.com** and sign up (free).
2. Click **"New +"** -> **"Web Service"**.

---

## Step 2 — Connect Your GitHub Repository

1. Select **"Build and deploy from a Git repository"**.
2. Connect your GitHub account if not already.
3. Search for **`Enterprise-Chatbot`** and click **"Connect"**.

---

## Step 3 — Configure the Web Service

Fill in the following settings in the Render dashboard:

| Field | Value |
|-------|-------|
| **Name** | `enterprise-rag-chatbot-backend` |
| **Region** | `Oregon (US West)` or nearest to you |
| **Branch** | `main` |
| **Runtime** | `Docker` |
| **Dockerfile Path** | `./backend/Dockerfile` |
| **Docker Context** | `.` (project root) |
| **Instance Type** | `Free` (or Starter $7/mo for no sleep) |

> **Free Tier Warning:** Free services spin down after 15 minutes of inactivity.
> First request after sleep takes ~30 seconds to wake up. Upgrade to Starter to avoid this.

---

## Step 4 — Configure Environment Variables

Go to **"Environment"** tab and add the following:

### Set Manually (your secrets)

| Key | Value |
|-----|-------|
| `NVIDIA_API_KEY` | Your key from https://build.nvidia.com |
| `SMTP_USER` | Your Gmail address |
| `SMTP_PASSWORD` | Your Gmail App Password (NOT your account password!) |

### Copy from `.env.example`

| Key | Value |
|-----|-------|
| `JWT_ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `OTP_EXPIRE_MINUTES` | `10` |
| `BACKEND_HOST` | `0.0.0.0` |
| `BACKEND_PORT` | `8000` |
| `FAISS_INDEX_PATH` | `/data/faiss_index` |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` |
| `NIM_MODEL` | `meta/llama-3.1-8b-instruct` |

### Auto-Generate

| Key | How |
|-----|-----|
| `JWT_SECRET_KEY` | Click **"Generate"** button in Render for a secure random value |
| `CORS_ORIGINS` | Set to `*` initially, update to your frontend URL later |

---

## Step 5 — Add Persistent Disk (for FAISS Index)

1. Scroll to **"Disks"** section in the service config.
2. Click **"Add Disk"**:
   - **Name:** `faiss-data`
   - **Mount Path:** `/data`
   - **Size:** `1 GB`

> This ensures your FAISS vector index persists across container restarts and deploys.
> NOTE: Persistent disks require a paid plan ($7/month minimum).

---

## Step 6 — Deploy

1. Click **"Create Web Service"**.
2. Render will:
   - Clone your GitHub repo
   - Build the Docker image (takes ~5-10 min first time)
   - Start the container
3. Watch the **"Logs"** tab for build progress.

---

## Step 7 — Verify Deployment

Once deploy is complete, visit your Render URL:

```
https://enterprise-rag-chatbot-backend.onrender.com/
```

Expected JSON response:
```json
{
  "status": "online",
  "service": "Enterprise RAG Chatbot API",
  "api_v1": "active"
}
```

Also check the interactive Swagger docs at:
```
https://enterprise-rag-chatbot-backend.onrender.com/docs
```

---

## Step 8 — Update CORS for Frontend

Once your frontend URL is live, update `CORS_ORIGINS` in Render env vars:
```
CORS_ORIGINS=https://your-frontend.vercel.app
```

---

## Common Issues and Fixes

| Issue | Fix |
|-------|-----|
| Build fails on pip install | Render can timeout on heavy installs; consider upgrading plan |
| FAISS import error on start | Ensure `libgomp1` is in Dockerfile (already present) |
| NVIDIA_API_KEY not found | Double-check env var name is exactly `NVIDIA_API_KEY` |
| Service keeps sleeping | Upgrade to Starter ($7/mo) or use https://cron-job.org to ping it |
| Disk not persisting data | Persistent disk requires paid plan; free tier is ephemeral |

---

## Gmail App Password Setup (for SMTP_PASSWORD)

Your `SMTP_PASSWORD` must be a Gmail **App Password**, not your regular account password:

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** if not already enabled
3. Search for **"App passwords"**
4. Create one: Mail -> Other -> name it `Render RAG Bot`
5. Copy the generated 16-character password into `SMTP_PASSWORD` in Render
