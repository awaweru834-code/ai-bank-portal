import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Pulls the PostgreSQL connection string from the environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/bankdb")

# New code
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,  # Tests the connection before using it. If dead, it reconnects automatically.
    pool_recycle=1800    # Proactively recycles connections every 30 minutes.
)

# 2. Configure session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Base class for SQLAlchemy ORM models[cite: 1]
Base = declarative_base()

# 4. Dependency generator to inject database sessions into FastAPI routers[cite: 1]
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()