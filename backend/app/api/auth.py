from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.middleware.auth import get_current_user, require_administrator
from app.models.user import User
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserOut
from app.services.audit_service import log_action
from app.services.auth_service import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.employee_code == payload.employee_code).first()
    if user is None or not user.is_active or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid employee code or password")

    token, minutes = create_access_token(user.id, user.role.value, extended=payload.stay_signed_in)
    log_action(db, user, "auth.login", "user", user.id)
    return TokenResponse(access_token=token, expires_in_minutes=minutes, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db), admin: User = Depends(require_administrator)):
    if db.query(User).filter(User.employee_code == payload.employee_code).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Employee code already in use")
    user = User(
        employee_code=payload.employee_code,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        jurisdiction=payload.jurisdiction,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    log_action(db, admin, "user.created", "user", user.id, notes=payload.employee_code)
    return user


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_administrator)):
    return db.query(User).order_by(User.full_name).all()
