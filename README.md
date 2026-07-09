# 🏦 Enterprise AI Bank Portal

A production-grade, Full-Stack AI banking application featuring stateless JWT authentication, a decoupled FastAPI backend, and an interactive Next.js RAG (Retrieval-Augmented Generation) assistant. 

## 🚀 Features

* **Dual-Brain AI Assistant:** Toggle between a secure "Bank Assistant" (with tool access to database balances) and a "Policy Checker" (RAG integration via Pinecone).
* **Enterprise Security:** Stateless JWT session management, robust 401 interceptors, and SlowAPI rate limiting (5 req/min).
* **Cold-Start Resilient UI:** Custom Next.js fetch interceptors that gracefully handle server wake-ups and network latency.
* **Vector Memory:** PDFs chunked and embedded via Pinecone for ultra-fast, context-aware policy retrieval.
* **Decoupled Architecture:** Next.js frontend and FastAPI backend designed to run independently or containerized via Docker.

## 🛠️ Tech Stack

**Frontend:** React, Next.js, Tailwind CSS
**Backend:** Python, FastAPI, SQLAlchemy, Passlib (Bcrypt)
**AI & Data:** Groq (Llama 3 8B), Pinecone (Vector DB), Neon (Serverless PostgreSQL)
**DevOps:** Docker, Uvicorn

## 🏗️ System Architecture

1. **The Client:** User interacts with a glass-morphism React UI.
2. **The Bridge:** `api.js` attaches JWT tokens to HTTP requests and catches standard/network errors.
3. **The Gateway:** FastAPI receives the request, verifies the JWT signature, and checks SlowAPI rate limits.
4. **The Brains:**
   * *Bank Mode:* AI logic fetches live balance data from PostgreSQL.
   * *Policy Mode:* AI logic fetches embedded vectors from Pinecone.
5. **The Delivery:** The unified JSON envelope is sent back to React for rendering.

## 💻 Local Quick Start

### 1. Start the Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
fastapi dev main.py
```

### 2. Start the Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```

Navigate to `http://localhost:3000` to access the secure vault.