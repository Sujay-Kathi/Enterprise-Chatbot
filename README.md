# 🚀 Enterprise RAG Chatbot

> ⚡ Enterprise-grade AI chatbot powered by **NVIDIA NIM + Llama 3.1 (8B)**

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge\&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?style=for-the-badge\&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red?style=for-the-badge\&logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue?style=for-the-badge\&logo=docker)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

---

## 🧠 Overview

An **enterprise-ready Retrieval-Augmented Generation (RAG) chatbot** that allows you to:

* Upload documents 📄
* Ask intelligent questions 🤖
* Get context-aware answers 💡

Built using **LangChain + NVIDIA NIM (Llama 3.1 8B)** with a secure and scalable architecture.

---

## ✨ Key Features

🔥 **Smart Document QA**
Upload PDFs & DOCX → get AI-powered answers instantly

🔐 **Secure Authentication**
Email OTP login system using SMTP

🛡️ **Content Moderation**
Filters harmful or inappropriate prompts

⚡ **High Performance Backend**
Powered by FastAPI + FAISS vector search

🐳 **Docker Ready**
One-command deployment

---

## 🏗️ Tech Stack

### 🔙 Backend

* FastAPI
* LangChain
* FAISS
* SentenceTransformers
* Uvicorn

### 🎨 Frontend

* Streamlit
* HTTPX / Requests

### 🔐 Security

* JWT Authentication
* Email OTP (SMTP)
* better-profanity

### ⚙️ Infrastructure

* Docker
* Docker Compose

---

## 📦 Installation Guide

### ✅ Prerequisites

Make sure you have:

* Python 3.11+
* Git
* *(Optional)* Docker Desktop

Also required:

* NVIDIA NIM API Key
* Email App Password

---

## ⚡ Quick Start

### 1️⃣ Clone the Repo

```bash
git clone https://github.com/Sujay-Kathi/Enterprise-Chatbot.git
cd Enterprise-Chatbot
```

---

### 2️⃣ Setup Environment Variables

```bash
cp .env.example .env
```

Update `.env`:

```env
NVIDIA_API_KEY=nvapi-xxxx
JWT_SECRET_KEY=your_secret_key

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
NIM_MODEL=meta/llama-3.1-8b-instruct
```

---

## ▶️ Run the App

### 🧑‍💻 Option A: Local Development

#### Terminal 1 – Backend

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows

pip install -r backend/requirements.txt
python backend/main.py
```

Backend → [http://localhost:8000](http://localhost:8000)

---

#### Terminal 2 – Frontend

```bash
.venv\Scripts\activate

pip install -r frontend/requirements.txt
streamlit run frontend/app.py
```

Frontend → [http://localhost:8501](http://localhost:8501)

---

### 🐳 Option B: Docker (Recommended 🚀)

```bash
docker-compose up --build
```

---

## 🧪 How to Use

1. Open → `http://localhost:8501`
2. Login using Email OTP
3. Upload documents 📂
4. Ask questions 💬
5. Get AI answers 🤖

---

## 📁 Project Structure

```
Enterprise-Chatbot/
│
├── backend/        # FastAPI + RAG logic
├── frontend/       # Streamlit UI
├── data/           # Vector DB & uploads
├── docker-compose.yml
└── .env
```

---

## 🤝 Contributing

We love contributions ❤️

```bash
# Fork the repo
# Create a new branch
git checkout -b feature/AmazingFeature

# Commit changes
git commit -m "Add AmazingFeature"

# Push
git push origin feature/AmazingFeature
```

Then open a Pull Request 🚀

---

## 📜 License

This project is licensed under the **MIT License**

---

## ⭐ Final Touch

If you like this project:

👉 Star the repo
👉 Share with others
👉 Build something cool

---
