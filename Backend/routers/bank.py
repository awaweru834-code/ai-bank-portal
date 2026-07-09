from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordRequestForm

# Import from your core and services folders
from core.database import get_db
from core.auth import verify_password, create_access_token
from core import models
from core.models import UserDB
from core import auth
from core.rate_limiter import limiter


# Create the router doorway (We remove the prefix here so we can specify exact paths below)
router = APIRouter(tags=["Banking"])

# ==========================================
# BOUNCERS (Pydantic Schemas)
# ==========================================
class UserCreate(BaseModel):
    username: str
    password: str = Field(max_length=72)
    balance: float



# ==========================================
# DOORWAYS (Endpoints)
# ==========================================
# DOORWAY 1: Sign Up
@router.post("/users/")
@limiter.limit("5/minute")
def create_user(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    
    # 1. 🛡️ The Bouncer Check: Does this username already exist?
    existing_user = db.query(models.UserDB).filter(models.UserDB.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username already registered. Please choose another."
        )

    # 2. 🔒 If they don't exist, hash the password and create the account
    hashed_pwd = auth.get_password_hash(user_data.password)
    
    new_user = models.UserDB(
        username=user_data.username,
        hashed_password=hashed_pwd, 
        balance=user_data.balance
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"User {new_user.username} securely created!"}



# DOORWAY 2: Check Profile (Locked with Auth)
@router.get("/users/me")
@limiter.limit("20/minute")
def read_my_profile(request: Request, username: str = Depends(auth.verify_token), db: Session = Depends(get_db)):
    user = db.query(models.UserDB).filter(models.UserDB.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    
    return {
        "id": user.id,
        "username": user.username,
        "balance": user.balance
    }
@router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # 1. Find the user in the database
    user = db.query(UserDB).filter(UserDB.username == form_data.username).first()
    
    # 2. Check if user exists AND the password matches
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Generate the JWT Token (putting the username inside the "sub" payload)
    access_token = create_access_token(data={"sub": user.username})
    
    # 4. Return it in the exact JSON format OAuth2 Swagger expects
    return {"access_token": access_token, "token_type": "bearer"}
    

