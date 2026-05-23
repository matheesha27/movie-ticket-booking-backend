from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.modules.users.model import User
from app.modules.auth.schema import RegisterRequest
from app.modules.auth.schema import LoginRequest
from app.modules.auth.security import hash_password
from app.modules.auth.security import verify_password
from app.modules.auth.service import create_access_token
from app.modules.auth.dependencies import get_current_user
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):

    print(request)
    print(request.password)

    existing_user = db.query(User).filter(
        User.email == request.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    hashed_password = hash_password(request.password)

    user = User(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        password_hash=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully"
    }

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    password_valid = verify_password(
        form_data.password,
        user.password_hash
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me")
def current_user(current_user = Depends(get_current_user)):

    return {
        "id": current_user.id,
        "email": current_user.email
    }
