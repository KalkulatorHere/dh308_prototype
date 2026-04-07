# ──────────────────────────────────────────────
# routes/vitals.py — Vitals recording routes
# GET/POST vitals per patient
# ──────────────────────────────────────────────

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user
from models import User, Vital, Patient
from schemas import VitalCreate, VitalOut
from middleware.consent_check import verify_consent

router = APIRouter(prefix="/api/patients", tags=["Vitals"])


@router.get("/{patient_id}/vitals", response_model=list[VitalOut])
def get_vitals(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all vitals for a patient, ordered by most recent."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Check access
    if current_user.role == "patient" and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot view another patient's vitals")
    elif current_user.role not in ("patient", "admin"):
        verify_consent(patient_id, db, current_user)

    vitals = db.query(Vital).filter(
        Vital.patient_id == patient_id
    ).order_by(Vital.recorded_at.desc()).all()

    return vitals


@router.post("/{patient_id}/vitals", response_model=VitalOut)
def create_vital(patient_id: int, req: VitalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Record new vitals for a patient. Doctors and patients can record."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Patients can only record their own vitals
    if current_user.role == "patient" and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot record vitals for another patient")
    elif current_user.role not in ("patient", "admin"):
        verify_consent(patient_id, db, current_user)

    vital = Vital(
        patient_id=patient_id,
        recorded_by=current_user.id,
        bp_systolic=req.bp_systolic,
        bp_diastolic=req.bp_diastolic,
        heart_rate=req.heart_rate,
        blood_sugar=req.blood_sugar,
        temperature=req.temperature,
        weight=req.weight,
        height=req.height,
        spo2=req.spo2
    )
    db.add(vital)
    db.commit()
    db.refresh(vital)
    return vital
