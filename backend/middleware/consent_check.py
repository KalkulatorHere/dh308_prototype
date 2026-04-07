# ──────────────────────────────────────────────
# middleware/consent_check.py — Consent verification dependency
# Ensures doctors have active consent before accessing patient data
# ──────────────────────────────────────────────

from datetime import datetime
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user
from models import User, Consent, Provider


def verify_consent(patient_id: int, db: Session, current_user: User) -> bool:
    """
    Check if the current user (doctor) has an active, non-expired consent
    to access the given patient's data. Patients can always access their own data.
    Admins bypass consent checks.
    """
    # Patients access their own data — always allowed
    if current_user.role == "patient":
        return True

    # Admins bypass consent checks
    if current_user.role == "admin":
        return True

    # Lab techs can upload but not view patient details without consent
    # Doctors must have active consent
    if current_user.role in ("doctor", "lab_tech"):
        provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Provider profile not found"
            )

        consent = db.query(Consent).filter(
            Consent.patient_id == patient_id,
            Consent.provider_id == provider.id,
            Consent.status == "approved"
        ).first()

        if not consent:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No active consent to access this patient's data"
            )

        # Check if consent has expired
        if consent.expires_at and consent.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Consent has expired. Request new consent from patient."
            )

        return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )
