# ──────────────────────────────────────────────
# routes/appointments.py — Appointment management
# GET (list), POST, PATCH status, DELETE
# ──────────────────────────────────────────────

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from dependencies import get_db, get_current_user
from models import User, Appointment, Provider, Patient
from schemas import AppointmentCreate, AppointmentOut

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])


@router.get("", response_model=list[AppointmentOut])
def list_appointments(
    patient_id: Optional[int] = Query(None),
    provider_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List appointments, filterable by patient and/or provider."""
    query = db.query(Appointment)

    # Patients see their own appointments
    if current_user.role == "patient":
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if patient:
            query = query.filter(Appointment.patient_id == patient.id)

    # Doctors see their own appointments
    elif current_user.role == "doctor":
        provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
        if provider:
            if patient_id:
                query = query.filter(Appointment.patient_id == patient_id, Appointment.provider_id == provider.id)
            else:
                query = query.filter(Appointment.provider_id == provider.id)

    # Admin can filter freely
    else:
        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)
        if provider_id:
            query = query.filter(Appointment.provider_id == provider_id)

    return query.order_by(Appointment.scheduled_at.desc()).all()


@router.post("", response_model=AppointmentOut)
def create_appointment(req: AppointmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Book a new appointment."""
    # Determine patient_id
    if current_user.role == "patient":
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient:
            raise HTTPException(status_code=400, detail="Patient profile not found")
        patient_id = patient.id
    elif req.patient_id:
        patient_id = req.patient_id
    else:
        raise HTTPException(status_code=400, detail="patient_id is required")

    # Verify provider exists
    provider = db.query(Provider).filter(Provider.id == req.provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    appointment = Appointment(
        patient_id=patient_id,
        provider_id=req.provider_id,
        appointment_type=req.appointment_type,
        scheduled_at=req.scheduled_at,
        duration_minutes=req.duration_minutes,
        notes=req.notes,
        meet_link=req.meet_link
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.patch("/{appointment_id}/status", response_model=AppointmentOut)
def update_appointment_status(
    appointment_id: int,
    status: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update appointment status (scheduled, completed, cancelled, no_show)."""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    valid_statuses = ["scheduled", "completed", "cancelled", "no_show"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {valid_statuses}")

    appointment.status = status
    db.commit()
    db.refresh(appointment)
    return appointment


@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Cancel/delete an appointment."""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Patients can only cancel their own
    if current_user.role == "patient":
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or appointment.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="Cannot cancel another patient's appointment")

    db.delete(appointment)
    db.commit()
    return {"detail": "Appointment deleted"}
