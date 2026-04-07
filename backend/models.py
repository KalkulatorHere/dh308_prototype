# ──────────────────────────────────────────────
# models.py — All SQLAlchemy ORM models for MediCore
# 11 tables: users, patients, providers, medical_records,
# vitals, prescriptions, lab_reports, lab_result_values,
# consents, appointments, audit_logs, notifications
# ──────────────────────────────────────────────

from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, Date,
    ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from database import Base

# ── User ──────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # patient | doctor | lab_tech | admin
    phone = Column(String(20), nullable=True)
    abha_id = Column(String(50), nullable=True)  # Ayushman Bharat Health Account
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient_profile = relationship("Patient", back_populates="user", uselist=False)
    provider_profile = relationship("Provider", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")


# ── Patient (extends User) ────────────────────
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    dob = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    blood_group = Column(String(10), nullable=True)
    allergies = Column(JSON, default=list)          # ["Penicillin", "Peanuts"]
    chronic_conditions = Column(JSON, default=list)  # ["Type 2 Diabetes"]
    emergency_contact = Column(JSON, default=dict)   # {name, phone, relation}

    # Relationships
    user = relationship("User", back_populates="patient_profile")
    medical_records = relationship("MedicalRecord", back_populates="patient")
    vitals = relationship("Vital", back_populates="patient")
    prescriptions = relationship("Prescription", back_populates="patient")
    lab_reports = relationship("LabReport", back_populates="patient")
    consents = relationship("Consent", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")


# ── Provider (Doctor / Lab Tech) ──────────────
class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    specialty = Column(String(100), nullable=True)
    hospital = Column(String(200), nullable=True)
    license_number = Column(String(50), nullable=True)

    # Relationships
    user = relationship("User", back_populates="provider_profile")
    medical_records = relationship("MedicalRecord", back_populates="provider")
    consents = relationship("Consent", back_populates="provider")
    appointments = relationship("Appointment", back_populates="provider")


# ── Medical Record ────────────────────────────
class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    record_type = Column(String(50), nullable=False)  # diagnosis | note | procedure | referral
    title = Column(String(255), nullable=False)
    icd10_code = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    extra_metadata = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    provider = relationship("Provider", back_populates="medical_records")


# ── Vitals ────────────────────────────────────
class Vital(Base):
    __tablename__ = "vitals"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    bp_systolic = Column(Integer, nullable=True)
    bp_diastolic = Column(Integer, nullable=True)
    heart_rate = Column(Integer, nullable=True)
    blood_sugar = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    spo2 = Column(Float, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="vitals")
    recorder = relationship("User", foreign_keys=[recorded_by])


# ── Prescription ──────────────────────────────
class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    drug_name = Column(String(200), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    duration = Column(String(100), nullable=True)
    instructions = Column(Text, nullable=True)
    status = Column(String(20), default="active")  # active | completed | cancelled
    dispensed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("Provider")


# ── Lab Report ────────────────────────────────
class LabReport(Base):
    __tablename__ = "lab_reports"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_name = Column(String(200), nullable=False)
    lab_name = Column(String(200), nullable=True)
    result_summary = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)  # Path to uploaded PDF
    status = Column(String(20), default="pending")   # pending | completed | reviewed
    report_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="lab_reports")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    result_values = relationship("LabResultValue", back_populates="report")


# ── Lab Result Value (individual parameters) ──
class LabResultValue(Base):
    __tablename__ = "lab_result_values"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("lab_reports.id"), nullable=False)
    parameter_name = Column(String(100), nullable=False)
    value = Column(String(50), nullable=False)
    unit = Column(String(30), nullable=True)
    reference_range = Column(String(50), nullable=True)
    is_abnormal = Column(Boolean, default=False)

    # Relationships
    report = relationship("LabReport", back_populates="result_values")


# ── Consent ───────────────────────────────────
class Consent(Base):
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    access_level = Column(String(20), nullable=False)  # full | view_only | emergency
    status = Column(String(20), default="pending")      # pending | approved | denied | revoked
    reason = Column(Text, nullable=True)
    granted_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="consents")
    provider = relationship("Provider", back_populates="consents")


# ── Appointment ───────────────────────────────
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    appointment_type = Column(String(30), nullable=False)  # video | in_person | lab
    scheduled_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    status = Column(String(20), default="scheduled")  # scheduled | completed | cancelled | no_show
    notes = Column(Text, nullable=True)
    meet_link = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    provider = relationship("Provider", back_populates="appointments")


# ── Audit Log ─────────────────────────────────
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, nullable=True)
    actor_type = Column(String(20), nullable=True)  # patient | doctor | lab_tech | admin | system
    action = Column(String(100), nullable=False)     # login | view_record | update_prescription ...
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(Integer, nullable=True)
    ip_address = Column(String(45), nullable=True)
    extra_metadata = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


# ── Notification ──────────────────────────────
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(50), nullable=False)   # consent_request | appointment_reminder | lab_result
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")
