# ──────────────────────────────────────────────
# schemas.py — Pydantic v2 request/response models
# ──────────────────────────────────────────────

from datetime import datetime, date
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr


# ── Auth ──────────────────────────────────────
class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str  # patient | doctor | lab_tech | admin
    phone: Optional[str] = None
    abha_id: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    user_id: int

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    phone: Optional[str] = None
    abha_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Patient ───────────────────────────────────
class PatientCreate(BaseModel):
    dob: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[List[str]] = []
    chronic_conditions: Optional[List[str]] = []
    emergency_contact: Optional[dict] = {}

class PatientUpdate(BaseModel):
    dob: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    emergency_contact: Optional[dict] = None

class PatientOut(BaseModel):
    id: int
    user_id: int
    dob: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[List[str]] = []
    chronic_conditions: Optional[List[str]] = []
    emergency_contact: Optional[dict] = {}
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True


# ── Provider ──────────────────────────────────
class ProviderCreate(BaseModel):
    specialty: Optional[str] = None
    hospital: Optional[str] = None
    license_number: Optional[str] = None

class ProviderOut(BaseModel):
    id: int
    user_id: int
    specialty: Optional[str] = None
    hospital: Optional[str] = None
    license_number: Optional[str] = None
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True


# ── Medical Record ────────────────────────────
class RecordCreate(BaseModel):
    patient_id: int
    record_type: str
    title: str
    icd10_code: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = {}

class RecordUpdate(BaseModel):
    record_type: Optional[str] = None
    title: Optional[str] = None
    icd10_code: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None

class RecordOut(BaseModel):
    id: int
    patient_id: int
    provider_id: Optional[int] = None
    record_type: str
    title: str
    icd10_code: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = {}
    created_at: datetime

    class Config:
        from_attributes = True


# ── Vitals ────────────────────────────────────
class VitalCreate(BaseModel):
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    blood_sugar: Optional[float] = None
    temperature: Optional[float] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    spo2: Optional[float] = None

class VitalOut(BaseModel):
    id: int
    patient_id: int
    recorded_by: Optional[int] = None
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    blood_sugar: Optional[float] = None
    temperature: Optional[float] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    spo2: Optional[float] = None
    recorded_at: datetime

    class Config:
        from_attributes = True


# ── Prescription ──────────────────────────────
class PrescriptionCreate(BaseModel):
    patient_id: int
    drug_name: str
    dosage: str
    frequency: str
    duration: Optional[str] = None
    instructions: Optional[str] = None
    expires_at: Optional[datetime] = None

class PrescriptionUpdate(BaseModel):
    status: Optional[str] = None
    instructions: Optional[str] = None
    dispensed_at: Optional[datetime] = None

class PrescriptionOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    drug_name: str
    dosage: str
    frequency: str
    duration: Optional[str] = None
    instructions: Optional[str] = None
    status: str
    dispensed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Lab Report ────────────────────────────────
class LabResultValueCreate(BaseModel):
    parameter_name: str
    value: str
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    is_abnormal: bool = False

class LabResultValueOut(BaseModel):
    id: int
    report_id: int
    parameter_name: str
    value: str
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    is_abnormal: bool

    class Config:
        from_attributes = True

class LabReportCreate(BaseModel):
    patient_id: int
    test_name: str
    lab_name: Optional[str] = None
    result_summary: Optional[str] = None
    report_date: Optional[date] = None
    result_values: Optional[List[LabResultValueCreate]] = []

class LabReportUpdate(BaseModel):
    status: Optional[str] = None
    result_summary: Optional[str] = None

class LabReportOut(BaseModel):
    id: int
    patient_id: int
    uploaded_by: int
    test_name: str
    lab_name: Optional[str] = None
    result_summary: Optional[str] = None
    file_path: Optional[str] = None
    status: str
    report_date: Optional[date] = None
    created_at: datetime
    result_values: List[LabResultValueOut] = []

    class Config:
        from_attributes = True


# ── Consent ───────────────────────────────────
class ConsentCreate(BaseModel):
    patient_id: int
    access_level: str  # full | view_only | emergency
    reason: Optional[str] = None
    expires_at: Optional[datetime] = None

class ConsentOut(BaseModel):
    id: int
    patient_id: int
    provider_id: int
    access_level: str
    status: str
    reason: Optional[str] = None
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Appointment ───────────────────────────────
class AppointmentCreate(BaseModel):
    patient_id: Optional[int] = None  # Optional so patients can book for themselves
    provider_id: int
    appointment_type: str  # video | in_person | lab
    scheduled_at: datetime
    duration_minutes: int = 30
    notes: Optional[str] = None
    meet_link: Optional[str] = None

class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    provider_id: int
    appointment_type: str
    scheduled_at: datetime
    duration_minutes: int
    status: str
    notes: Optional[str] = None
    meet_link: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Audit Log ─────────────────────────────────
class AuditLogOut(BaseModel):
    id: int
    actor_id: Optional[int] = None
    actor_type: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    ip_address: Optional[str] = None
    metadata: Optional[dict] = {}
    created_at: datetime

    class Config:
        from_attributes = True


# ── Notification ──────────────────────────────
class NotificationOut(BaseModel):
    id: int
    user_id: int
    type: str
    title: str
    body: Optional[str] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Admin ─────────────────────────────────────
class AdminStatsOut(BaseModel):
    total_patients: int
    total_providers: int
    total_records: int
    total_prescriptions: int
    total_lab_reports: int
    total_appointments: int
    pending_consents: int

class AdminUserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str
    phone: Optional[str] = None

class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    phone: Optional[str] = None
