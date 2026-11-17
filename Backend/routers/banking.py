from core import auth, models
from core.auth import verify_password
from core.database import get_db
from core.rate_limiter import limiter
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(tags=["Banking"])
@router.post("/login") # or "/token" depending on what you named it
def login_for_access_token(
    response: Response, # <-- We inject the Response object here
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
    
    # 4. Set the secure HttpOnly cookie instead of sending it in the body
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,      # Protects against XSS attacks
        secure=False,       # Keep False for localhost testing. Change to True on Render/HTTPS.
        samesite="lax",     # Protects against CSRF attacks
        max_age=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    # 5. Return a safe success payload (the browser automatically stores the cookie)
    return {"message": "Login successful", "user_id": user.id}

@router.delete("/users/delete")
def delete_account(
    response: Response,
    current_user: models.UserDB = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db.delete(current_user)
    db.commit()
    
    response.delete_cookie("access_token", httponly=True, samesite="lax")
    return {"message": "Account securely deleted and session terminated"}
# Pydantic schema for input validation - Username and Password only
class UserCreate(BaseModel):
    username: str
    password: str

@router.post("/users/")
@limiter.limit("5/minute")
def create_user(
    request: Request, # Required by slowapi
    user_data: UserCreate, 
    db: Session = Depends(get_db)
):
    # 1. Check if username already exists
    existing_user = db.query(models.UserDB).filter(models.UserDB.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered. Please choose another."
        )

    # 2. Hash password and create account
    hashed_pwd = auth.get_password_hash(user_data.password)
    
    new_user = models.UserDB(
        username=user_data.username,
        hashed_password=hashed_pwd,
        # Default balance is handled by the model definition (1000.0)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": f"User {new_user.username} securely created!"}
# Add this to routers/banking.py
@router.get("/users/me")
def read_my_profile(
    current_user: models.UserDB = Depends(auth.get_current_user)
):
    # Returns the user's profile and balance to the frontend dashboard
    return {
        "id": current_user.id,
        "username": current_user.username,
        "balance": current_user.balance
    }