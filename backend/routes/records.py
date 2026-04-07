# ──────────────────────────────────────────────
# routes/records.py — Medical Records CRUD
# GET (list/filter), POST, GET/:id, PUT/:id, DELETE/:id
# ──────────────────────────────────────────────

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from dependencies import get_db, get_current_user
from models import User, MedicalRecord, Provider, Patient
from schemas import RecordCreate, RecordUpdate, RecordOut
from middleware.consent_check import verify_consent

router = APIRouter(prefix="/api/records", tags=["Medical Records"])


@router.get("", response_model=list[RecordOut])
def list_records(
    patient_id: Optional[int] = Query(None),
    type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List medical records, optionally filtered by patient and/or type."""
    query = db.query(MedicalRecord)

    # Patients can only see their own records
    if current_user.role == "patient":
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if patient:
            query = query.filter(MedicalRecord.patient_id == patient.id)

    elif patient_id:
        verify_consent(patient_id, db, current_user)
        query = query.filter(MedicalRecord.patient_id == patient_id)

    if type:
        query = query.filter(MedicalRecord.record_type == type)

    return query.order_by(MedicalRecord.created_at.desc()).all()


@router.post("", response_model=RecordOut)
def create_record(req: RecordCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new medical record. Doctors only."""
    if current_user.role not in ("doctor", "admin"):
        raise HTTPException(status_code=403, detail="Only doctors can create medical records")

    verify_consent(req.patient_id, db, current_user)

    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()

    record = MedicalRecord(
        patient_id=req.patient_id,
        provider_id=provider.id if provider else None,
        record_type=req.record_type,
        title=req.title,
        icd10_code=req.icd10_code,
        notes=req.notes,
        metadata=req.metadata
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{record_id}", response_model=RecordOut)
def get_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get a single medical record by ID."""
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    verify_consent(record.patient_id, db, current_user)
    return record


@router.put("/{record_id}", response_model=RecordOut)
def update_record(record_id: int, req: RecordUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update a medical record. Only the creating doctor or admin."""
    if current_user.role not in ("doctor", "admin"):
        raise HTTPException(status_code=403, detail="Only doctors can update records")

    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    update_data = req.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a medical record. Admin only."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete records")

    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    db.delete(record)
    db.commit()
    return {"detail": "Record deleted"}
