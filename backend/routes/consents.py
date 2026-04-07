# ──────────────────────────────────────────────
# routes/consents.py — Consent management
# POST (request), PATCH approve/deny/revoke, GET (list)
# ──────────────────────────────────────────────

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from dependencies import get_db, get_current_user
from models import User, Consent, Provider, Patient, Notification
from schemas import ConsentCreate, ConsentOut

router = APIRouter(prefix="/api/consents", tags=["Consents"])


@router.get("", response_model=list[ConsentOut])
def list_consents(
    patient_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List consents, filterable by patient and status."""
    query = db.query(Consent)

    # Patients see their own consents
    if current_user.role == "patient":
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if patient:
            query = query.filter(Consent.patient_id == patient.id)

    # Doctors see consents where they are the provider
    elif current_user.role == "doctor":
        provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
        if provider:
            if patient_id:
                query = query.filter(Consent.patient_id == patient_id, Consent.provider_id == provider.id)
            else:
                query = query.filter(Consent.provider_id == provider.id)

    # Admin sees all; optionally filter
    elif current_user.role == "admin" and patient_id:
        query = query.filter(Consent.patient_id == patient_id)

    if status:
        query = query.filter(Consent.status == status)

    return query.order_by(Consent.created_at.desc()).all()


@router.post("", response_model=ConsentOut)
def create_consent(req: ConsentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Request consent to access a patient's data. Doctors create requests."""
    if current_user.role not in ("doctor", "admin"):
        raise HTTPException(status_code=403, detail="Only doctors can request consent")

    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=400, detail="Provider profile not found")

    # Check for existing active or pending consent
    existing = db.query(Consent).filter(
        Consent.patient_id == req.patient_id,
        Consent.provider_id == provider.id,
        Consent.status.in_(["pending", "approved"])
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail=f"Consent already exists with status: {existing.status}")

    consent = Consent(
        patient_id=req.patient_id,
        provider_id=provider.id,
        access_level=req.access_level,
        reason=req.reason,
        expires_at=req.expires_at,
        status="pending"
    )
    db.add(consent)

    # Create notification for the patient
    patient = db.query(Patient).filter(Patient.id == req.patient_id).first()
    if patient:
        notification = Notification(
            user_id=patient.user_id,
            type="consent_request",
            title="New Consent Request",
            body=f"Dr. {current_user.full_name} is requesting {req.access_level} access to your records."
        )
        db.add(notification)

    db.commit()
    db.refresh(consent)
    return consent


@router.patch("/{consent_id}/approve", response_model=ConsentOut)
def approve_consent(consent_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Approve a consent request. Patients only."""
    consent = db.query(Consent).filter(Consent.id == consent_id).first()
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")

    # Only the patient can approve
    patient = db.query(Patient).filter(Patient.id == consent.patient_id).first()
    if current_user.role != "admin" and (not patient or patient.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Only the patient can approve consents")

    consent.status = "approved"
    consent.granted_at = datetime.utcnow()
    db.commit()
    db.refresh(consent)
    return consent


@router.patch("/{consent_id}/deny", response_model=ConsentOut)
def deny_consent(consent_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Deny a consent request. Patients only."""
    consent = db.query(Consent).filter(Consent.id == consent_id).first()
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")

    patient = db.query(Patient).filter(Patient.id == consent.patient_id).first()
    if current_user.role != "admin" and (not patient or patient.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Only the patient can deny consents")

    consent.status = "denied"
    db.commit()
    db.refresh(consent)
    return consent


@router.patch("/{consent_id}/revoke", response_model=ConsentOut)
def revoke_consent(consent_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Revoke an active consent. Patients only."""
    consent = db.query(Consent).filter(Consent.id == consent_id).first()
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")

    patient = db.query(Patient).filter(Patient.id == consent.patient_id).first()
    if current_user.role != "admin" and (not patient or patient.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Only the patient can revoke consents")

    consent.status = "revoked"
    consent.revoked_at = datetime.utcnow()
    db.commit()
    db.refresh(consent)
    return consent
