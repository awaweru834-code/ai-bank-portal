import os

from core import models
from core.database import engine

# Your decoupled modules
from core.rate_limiter import limiter
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import ai_chat, banking
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

load_dotenv()

# Creates the tables in PostgreSQL automatically on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hank Bank API")

# 1. Attach the Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2. Secure CORS Middleware for HttpOnly Cookies
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "http://127.0.0.1:5173",
                   "https://ai-bank-portal.vercel.app"
                   ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Mount Routers
app.include_router(banking.router)
app.include_router(ai_chat.router)