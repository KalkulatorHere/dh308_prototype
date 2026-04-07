# ──────────────────────────────────────────────
# routes/patients.py — Patient profile routes
# GET/PUT patient profile, summary, timeline
# ──────────────────────────────────────────────

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from dependencies import get_db, get_current_user
from models import User, Patient, MedicalRecord, Vital, Prescription, LabReport, Appointment, Consent
from schemas import PatientOut, PatientUpdate
from middleware.consent_check import verify_consent

router = APIRouter(prefix="/api/patients", tags=["Patients"])


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get a patient's profile. Consent-gated for doctors."""
    patient = db.query(Patient).options(joinedload(Patient.user)).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Consent check for non-patient roles
    if current_user.role != "patient" or patient.user_id != current_user.id:
        verify_consent(patient_id, db, current_user)

    return patient


@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: int, req: PatientUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update patient profile. Only the patient themselves or admin."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Only the patient or admin can update
    if current_user.role == "patient" and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot update another patient's profile")
    if current_user.role not in ("patient", "admin"):
        raise HTTPException(status_code=403, detail="Only patients and admins can update profiles")

    # Update fields
    update_data = req.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)
    return patient


@router.get("/{patient_id}/summary")
def get_patient_summary(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get a patient's health summary — vitals, active Rx, upcoming appts, pending consents."""
    patient = db.query(Patient).options(joinedload(Patient.user)).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if current_user.role != "patient" or patient.user_id != current_user.id:
        verify_consent(patient_id, db, current_user)

    # Latest vitals
    latest_vital = db.query(Vital).filter(Vital.patient_id == patient_id).order_by(Vital.recorded_at.desc()).first()

    # Active prescriptions count
    active_rx = db.query(Prescription).filter(
        Prescription.patient_id == patient_id,
        Prescription.status == "active"
    ).count()

    # Upcoming appointments
    from datetime import datetime
    upcoming_appts = db.query(Appointment).filter(
        Appointment.patient_id == patient_id,
        Appointment.status == "scheduled",
        Appointment.scheduled_at >= datetime.utcnow()
    ).count()

    # Pending consents
    pending_consents = db.query(Consent).filter(
        Consent.patient_id == patient_id,
        Consent.status == "pending"
    ).count()

    # Recent records count
    total_records = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).count()

    return {
        "patient": PatientOut.model_validate(patient),
        "latest_vitals": latest_vital,
        "active_prescriptions": active_rx,
        "upcoming_appointments": upcoming_appts,
        "pending_consents": pending_consents,
        "total_records": total_records
    }


@router.get("/{patient_id}/timeline")
def get_patient_timeline(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get a chronological timeline of all health events for a patient."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if current_user.role != "patient" or patient.user_id != current_user.id:
        verify_consent(patient_id, db, current_user)

    # Collect all timeline events
    events = []

    # Medical records
    records = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).all()
    for r in records:
        events.append({"type": "record", "subtype": r.record_type, "title": r.title, "date": r.created_at.isoformat(), "id": r.id})

    # Prescriptions
    prescriptions = db.query(Prescription).filter(Prescription.patient_id == patient_id).all()
    for p in prescriptions:
        events.append({"type": "prescription", "title": f"{p.drug_name} — {p.dosage}", "date": p.created_at.isoformat(), "id": p.id, "status": p.status})

    # Lab reports
    labs = db.query(LabReport).filter(LabReport.patient_id == patient_id).all()
    for l in labs:
        events.append({"type": "lab_report", "title": l.test_name, "date": l.created_at.isoformat(), "id": l.id, "status": l.status})

    # Appointments
    appts = db.query(Appointment).filter(Appointment.patient_id == patient_id).all()
    for a in appts:
        events.append({"type": "appointment", "title": f"{a.appointment_type} appointment", "date": a.scheduled_at.isoformat(), "id": a.id, "status": a.status})

    # Vitals
    vitals = db.query(Vital).filter(Vital.patient_id == patient_id).all()
    for v in vitals:
        events.append({"type": "vitals", "title": "Vitals recorded", "date": v.recorded_at.isoformat(), "id": v.id})

    # Sort by date descending
    events.sort(key=lambda x: x["date"], reverse=True)

    return events
