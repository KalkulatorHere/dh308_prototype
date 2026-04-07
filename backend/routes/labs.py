# ──────────────────────────────────────────────
# routes/labs.py — Lab Report management
# GET (list), POST (upload), GET/:id, PUT/:id, GET/:id/download
# ──────────────────────────────────────────────

import os
import shutil
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from dependencies import get_db, get_current_user
from models import User, LabReport, LabResultValue, Patient
from schemas import LabReportOut, LabReportUpdate, LabResultValueCreate
from middleware.consent_check import verify_consent

router = APIRouter(prefix="/api/lab-reports", tags=["Lab Reports"])

# Upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("", response_model=list[LabReportOut])
def list_lab_reports(
    patient_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List lab reports, optionally filtered by patient."""
    query = db.query(LabReport)

    if current_user.role == "patient":
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if patient:
            query = query.filter(LabReport.patient_id == patient.id)
    elif patient_id:
        verify_consent(patient_id, db, current_user)
        query = query.filter(LabReport.patient_id == patient_id)

    return query.order_by(LabReport.created_at.desc()).all()


@router.post("", response_model=LabReportOut)
async def create_lab_report(
    patient_id: int = Form(...),
    test_name: str = Form(...),
    lab_name: Optional[str] = Form(None),
    result_summary: Optional[str] = Form(None),
    report_date: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a new lab report with optional PDF file."""
    if current_user.role not in ("lab_tech", "doctor", "admin"):
        raise HTTPException(status_code=403, detail="Only lab techs can upload reports")

    # Save uploaded PDF
    file_path = None
    if file:
        filename = f"lab_{patient_id}_{test_name.replace(' ', '_')}_{date.today().isoformat()}.pdf"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        file_path = f"/uploads/{filename}"

    parsed_date = None
    if report_date:
        try:
            parsed_date = date.fromisoformat(report_date)
        except ValueError:
            parsed_date = date.today()

    report = LabReport(
        patient_id=patient_id,
        uploaded_by=current_user.id,
        test_name=test_name,
        lab_name=lab_name,
        result_summary=result_summary,
        file_path=file_path,
        report_date=parsed_date,
        status="completed"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/{report_id}", response_model=LabReportOut)
def get_lab_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get a single lab report with result values."""
    report = db.query(LabReport).filter(LabReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Lab report not found")

    verify_consent(report.patient_id, db, current_user)
    return report


@router.put("/{report_id}", response_model=LabReportOut)
def update_lab_report(report_id: int, req: LabReportUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update lab report status/summary."""
    if current_user.role not in ("lab_tech", "doctor", "admin"):
        raise HTTPException(status_code=403, detail="Only lab techs can update reports")

    report = db.query(LabReport).filter(LabReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Lab report not found")

    update_data = req.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)

    db.commit()
    db.refresh(report)
    return report


@router.post("/{report_id}/values")
def add_result_values(
    report_id: int,
    values: list[LabResultValueCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add result values to a lab report."""
    if current_user.role not in ("lab_tech", "doctor", "admin"):
        raise HTTPException(status_code=403, detail="Only lab techs can add results")

    report = db.query(LabReport).filter(LabReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Lab report not found")

    for val in values:
        result = LabResultValue(
            report_id=report_id,
            parameter_name=val.parameter_name,
            value=val.value,
            unit=val.unit,
            reference_range=val.reference_range,
            is_abnormal=val.is_abnormal
        )
        db.add(result)

    db.commit()
    return {"detail": f"Added {len(values)} result values"}


@router.get("/{report_id}/download")
def download_lab_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Download the lab report PDF file."""
    report = db.query(LabReport).filter(LabReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Lab report not found")

    verify_consent(report.patient_id, db, current_user)

    if not report.file_path:
        raise HTTPException(status_code=404, detail="No file attached to this report")

    # Convert relative path to absolute
    abs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), report.file_path.lstrip("/"))
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="File not found on server")

    return FileResponse(abs_path, media_type="application/pdf", filename=os.path.basename(abs_path))
