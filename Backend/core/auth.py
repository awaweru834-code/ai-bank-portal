import os
from datetime import datetime, timedelta, timezone

import bcrypt

# 1. Import your database connection and models so the bouncer can look up users
from core.database import get_db
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status

from fastapi.security import APIKeyCookie
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from core import models

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30 

# ==========================================
# PASSWORD HASHING
# ==========================================
def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)

# ==========================================
# TOKEN CREATION
# ==========================================
def create_access_token(data: dict):
    to_encode = data.copy()
    
    # FIX: Use timezone.utc instead of the deprecated utcnow()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ==========================================
# THE BOUNCER (Dependency)
# ==========================================
# 2. Tell FastAPI to look for a cookie named "access_token" instead of a header
cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)

def get_current_user(token: str = Depends(cookie_scheme), db: Session = Depends(get_db)):
    """
    This function intercepts the request, grabs the token from the HTTP cookie,
    decodes it, and fetches the live user from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    
    # 3. If no cookie is found, kick them out
    if not token:
        raise credentials_exception
        
    try:
        # 4. Open the wristband (Remove "Bearer " if you stored it with the prefix)
        clean_token = token.replace("Bearer ", "") if token.startswith("Bearer ") else token
        payload = jwt.decode(clean_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception

    user = db.query(models.UserDB).filter(models.UserDB.username == username).first()
    
    if user is None:
        raise credentials_exception
        
    return user