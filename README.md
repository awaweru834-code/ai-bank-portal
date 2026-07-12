# Enterprise AI Bank Portal

🚀 **Live Demo:** [Add your Vercel Link Here]

* screenshot 
LogIn portal
<img width="958" height="436" alt="image" src="https://github.com/user-attachments/assets/230b3dac-891e-4d70-b9a6-c47158189185" />
The AI-chat
<img width="953" height="431" alt="image" src="https://github.com/user-attachments/assets/25f2fdbd-71de-4ab0-9b6f-2245d472c272" />
The AI_policy_checker
<img width="959" height="437" alt="image" src="https://github.com/user-attachments/assets/ee4400e9-b6a4-4eb3-81da-bfa19b582eff" />


A full-stack banking application built to explore the challenges of integrating Large Language Models (LLMs) with secure, traditional database systems. 

I built this project to move beyond simple AI chat scripts and architect a decoupled, production-ready system. The core challenge was ensuring the AI could seamlessly toggle between pulling live, private data from a SQL database (user balances) and querying a vector database (Pinecone) for static RAG policy documents, all while protected by strict JWT authentication.

## 🛠️ Core Architecture

* **Frontend (Next.js & Tailwind):** A stateless React interface featuring custom fetch interceptors to gracefully handle server wake-ups and network latency.
* **Backend (FastAPI & Python):** A decoupled API using SQLAlchemy for database operations and Passlib/Bcrypt for password hashing.
* **AI Engine (Groq Llama 3):** Routes natural language queries to the correct tool (PostgreSQL or Pinecone) based on user intent.
* **Security & Infrastructure:** Implements stateless JWT session management and SlowAPI rate limiting (5 req/min) to prevent abuse. Containerized using Docker for deployment consistency.

## 🧠 How the System Works

1. **The Request:** The Next.js frontend attaches the user's JWT token to the HTTP request.
2. **The Gateway:** FastAPI intercepts the request, verifies the JWT signature, and checks the rate limits.
3. **The Engine:**
   * If querying a balance, the AI executes a secure tool call to the Neon PostgreSQL database.
   * If asking a policy question, the AI retrieves chunked, embedded vectors from Pinecone.
4. **The Response:** The final AI context is packaged into a unified JSON envelope and rendered in the React UI.

## 🚧 Challenges & Learnings

* **Git Submodule Traps:** While structuring the monorepo, I accidentally initialized nested `.git` folders within the frontend and backend directories. I had to manually clear the git cache and remove the hidden tracking folders to ensure a clean push to origin.
* **Windows vs. Linux Pathing:** Encountered discrepancies between generic documentation and my local Windows environment, requiring me to adapt my virtual environment activation (`.\venv\Scripts\activate`) and standardize line endings (LF to CRLF) for Git compatibility.
* **Stateless Memory:** Moving away from global dictionaries to storing conversation history directly in PostgreSQL taught me a lot about maintaining state in a decoupled REST API.

## 💻 Local Quick Start

### 1. Start the Backend (FastAPI)
Open your terminal and navigate to the backend folder:
```bash
cd Backend
```

Create and activate your virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

Boot up the development server:
```bash
fastapi dev main.py
```
*The API will be available at `http://localhost:8000` and the interactive Swagger docs at `http://localhost:8000/docs`.*

---

### 2. Start the Frontend (Next.js)
Open a **second** terminal window and navigate to the frontend folder:
```bash
cd frontend
```

Install the Node modules:
```bash
npm install
```

Start the React development server:
```bash
npm run dev
```
*The web interface will be available at `http://localhost:3000`.*
