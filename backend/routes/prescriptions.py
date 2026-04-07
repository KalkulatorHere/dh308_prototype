# ──────────────────────────────────────────────
# routes/prescriptions.py — Prescription management
# GET (list), POST, PUT (update status)
# ──────────────────────────────────────────────

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from dependencies import get_db, get_current_user
from models import User, Prescription, Provider, Patient
from schemas import PrescriptionCreate, PrescriptionUpdate, PrescriptionOut
from middleware.consent_check import verify_consent

router = APIRouter(prefix="/api/prescriptions", tags=["Prescriptions"])


@router.get("", response_model=list[PrescriptionOut])
def list_prescriptions(
    patient_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List prescriptions, optionally filtered by patient."""
    query = db.query(Prescription)

    # Patients can only see their own
    if current_user.role == "patient":
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if patient:
            query = query.filter(Prescription.patient_id == patient.id)
    elif patient_id:
        verify_consent(patient_id, db, current_user)
        query = query.filter(Prescription.patient_id == patient_id)

    return query.order_by(Prescription.created_at.desc()).all()


@router.post("", response_model=PrescriptionOut)
def create_prescription(
    req: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new prescription. Doctors only."""
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can prescribe")

    verify_consent(req.patient_id, db, current_user)

    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=400, detail="Provider profile not found")

    prescription = Prescription(
        patient_id=req.patient_id,
        doctor_id=provider.id,
        drug_name=req.drug_name,
        dosage=req.dosage,
        frequency=req.frequency,
        duration=req.duration,
        instructions=req.instructions,
        expires_at=req.expires_at
    )
    db.add(prescription)
    db.commit()
    db.refresh(prescription)
    return prescription


@router.put("/{prescription_id}", response_model=PrescriptionOut)
def update_prescription(
    prescription_id: int,
    req: PrescriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a prescription (status, instructions). Doctors/admins only."""
    if current_user.role not in ("doctor", "admin"):
        raise HTTPException(status_code=403, detail="Only doctors can update prescriptions")

    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    update_data = req.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prescription, field, value)

    db.commit()
    db.refresh(prescription)
    return prescription
