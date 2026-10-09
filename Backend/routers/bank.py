from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# Cleaned up imports
from core import auth, models
from core.database import get_db
from core.rate_limiter import limiter

# Create the router doorway
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
def read_my_profile(
    request: Request, 
    current_user: models.UserDB = Depends(auth.get_current_user) # FIX: Accept the full user object
):
    # FIX: The bouncer (auth.py) already verified the token and fetched the user from the DB.
    # We can skip the extra database query and just return the data directly.
    return {
        "id": current_user.id,
        "username": current_user.username,
        "balance": current_user.balance
    }


# DOORWAY 3: Login & Set Cookie
@router.post("/token")
def login_for_access_token(
    response: Response, # FIX: Inject Response to set the cookie
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # 1. Find the user in the database
    user = db.query(models.UserDB).filter(models.UserDB.username == form_data.username).first()
    
    # 2. Verify existence and password
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Generate the JWT Token
    access_token = auth.create_access_token(data={"sub": user.username})
    
    # 4. FIX: Set the secure HttpOnly cookie instead of sending it in the body
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,      # Protects against XSS
        secure=False,       # Set to True when you deploy with HTTPS
        samesite="lax",     # Protects against CSRF
        max_age=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    # 5. Return a safe success payload
    return {"message": "Login successful", "user_id": user.id}
@router.delete("/users/me")
def delete_my_account(
    response: Response,
    current_user: models.UserDB = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Delete the user from the database (Cascades will handle their chat history if configured)
    db.delete(current_user)
    db.commit()
    
    # 2. Instruct the browser to destroy the secure cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False, # Match the secure setting from your login route
        samesite="lax"
    )
    
    return {"message": "Account securely deleted and session terminated"}