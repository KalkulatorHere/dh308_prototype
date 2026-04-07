# ──────────────────────────────────────────────
# routes/admin.py — Admin dashboard routes
# Stats, audit logs (paginated), user CRUD
# ──────────────────────────────────────────────

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dependencies import get_db, require_role
from models import User, Patient, Provider, MedicalRecord, Prescription, LabReport, Appointment, Consent, AuditLog
from schemas import AdminStatsOut, AdminUserCreate, AdminUserUpdate, UserOut, AuditLogOut
from auth import hash_password

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminStatsOut)
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    """Get system-wide statistics."""
    return AdminStatsOut(
        total_patients=db.query(Patient).count(),
        total_providers=db.query(Provider).count(),
        total_records=db.query(MedicalRecord).count(),
        total_prescriptions=db.query(Prescription).count(),
        total_lab_reports=db.query(LabReport).count(),
        total_appointments=db.query(Appointment).count(),
        pending_consents=db.query(Consent).filter(Consent.status == "pending").count()
    )


@router.get("/audit-logs", response_model=list[AuditLogOut])
def get_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    actor_id: int = Query(None),
    action: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Get paginated audit logs, filterable by actor and action."""
    query = db.query(AuditLog)

    if actor_id:
        query = query.filter(AuditLog.actor_id == actor_id)
    if action:
        query = query.filter(AuditLog.action.contains(action))

    offset = (page - 1) * limit
    return query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    """List all users."""
    return db.query(User).order_by(User.created_at.desc()).all()


@router.post("/users", response_model=UserOut)
def create_user(req: AdminUserCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    """Admin creates a new user."""
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        full_name=req.full_name,
        email=req.email,
        password_hash=hash_password(req.password),
        role=req.role,
        phone=req.phone
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Auto-create profile
    if req.role == "patient":
        db.add(Patient(user_id=user.id))
        db.commit()
    elif req.role in ("doctor", "lab_tech"):
        db.add(Provider(user_id=user.id))
        db.commit()

    return user


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, req: AdminUserUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    """Admin updates a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = req.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user
