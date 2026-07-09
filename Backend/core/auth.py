import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
import os
from dotenv import load_dotenv

load_dotenv()
# Fetch the variables safely
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# We can provide a default fallback for the algorithm just in case
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# 1. Function to scramble a plain text password
def get_password_hash(password: str):
    # Bcrypt requires passwords to be encoded as bytes before hashing
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    
    # Return it as a normal string so we can save it in the database
    return hashed_password.decode('utf-8')

# 2. Function to check if a typed password matches the database
def verify_password(plain_password: str, hashed_password: str):
    password_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hash_bytes)

ACCESS_TOKEN_EXPIRE_MINUTES = 30 # The wristband expires in 30 minutes

def create_access_token(data: dict):
    # 1. Copy the data (usually just the username)
    to_encode = data.copy()
    
    # 2. Calculate the exact time this token should expire
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 3. Add the expiration time to the data
    to_encode.update({"exp": expire})
    
    # 4. Use the JOSE library to digitally sign and create the JWT!
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt
# 1. This tells FastAPI where the "Ticket Booth" is
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 2. This is the BOUNCER that stands in front of your locked doors
def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Open the wristband using our secret company key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Pull the username out of the wristband
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
        # Hand the verified username back to the API!
        return username
        
    except JWTError:
        # If the token is fake, expired, or tampered with, kick them out!
        raise credentials_exception