import os
from datetime import datetime, timedelta, timezone, UTC

import bcrypt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyCookie
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from core import models
from core.database import get_db

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
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ==========================================
# THE BOUNCER (Dependency)
# ==========================================
# 1. Instruct FastAPI to look in the cookie jar for "access_token"
cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)

def get_current_user(token: str = Depends(cookie_scheme), db: Session = Depends(get_db)):
    """
    Intercepts the request, extracts the JWT from the HttpOnly cookie,
    validates the signature, and returns the live database user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    
    # 2. If the browser didn't send the cookie, reject the request
    if not token:
        raise credentials_exception
        
    try:
        # 3. Open the cryptographically signed wristband
        clean_token = token.replace("Bearer ", "") if token.startswith("Bearer ") else token
        payload = jwt.decode(clean_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except JWTError:
        # Fails if the token is expired or was tampered with
        raise credentials_exception

    # 4. Fetch the verified user from PostgreSQL
    user = db.query(models.UserDB).filter(models.UserDB.username == username).first()
    
    if user is None:
        raise credentials_exception
        
    return user