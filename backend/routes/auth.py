# ──────────────────────────────────────────────
# routes/auth.py — Authentication routes
# POST /api/auth/register, POST /api/auth/login, GET /api/auth/me
# ──────────────────────────────────────────────

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user
from models import User, Patient, Provider
from schemas import RegisterRequest, LoginRequest, TokenResponse, UserOut
from auth import hash_password, verify_password, create_access_token, create_refresh_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with email + password."""
    # Check if email already exists
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate role
    valid_roles = ["patient", "doctor", "lab_tech", "admin"]
    if req.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Role must be one of: {valid_roles}")

    # Create user
    user = User(
        full_name=req.full_name,
        email=req.email,
        password_hash=hash_password(req.password),
        role=req.role,
        phone=req.phone,
        abha_id=req.abha_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Auto-create patient or provider profile
    if req.role == "patient":
        patient = Patient(user_id=user.id)
        db.add(patient)
        db.commit()
    elif req.role in ("doctor", "lab_tech"):
        provider = Provider(user_id=user.id)
        db.add(provider)
        db.commit()

    # Generate tokens
    token_data = {"sub": str(user.id), "role": user.role, "email": user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role,
        user_id=user.id
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with email + password, receive JWT tokens."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token_data = {"sub": str(user.id), "role": user.role, "email": user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role,
        user_id=user.id
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return current_user
