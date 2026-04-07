# ──────────────────────────────────────────────
# seed.py — Populate demo data
# Patient: Rahul Sharma, 42M, B+, Type 2 Diabetes + Hypertension
# Doctors: Dr. Priya Mehta (Endocrinology), Dr. Arjun Rao (General)
# Lab Tech: Neha Singh
# Admin: System Admin
# ──────────────────────────────────────────────

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, date, timedelta
from database import SessionLocal, engine, Base
from models import (
    User, Patient, Provider, MedicalRecord, Vital,
    Prescription, LabReport, LabResultValue, Consent,
    Appointment, Notification
)
from auth import hash_password

# Create all tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # ── Check if already seeded ───────────────
    if db.query(User).first():
        print("Database already seeded. Delete medicore.db to reseed.")
        sys.exit(0)

    print("Seeding MediCore database...")

    # ── Users ─────────────────────────────────
    patient_user = User(
        full_name="Rahul Sharma",
        email="rahul@medicore.com",
        password_hash=hash_password("password123"),
        role="patient",
        phone="+91 98765 43210",
        abha_id="ABHA-1234-5678-9012"
    )

    doctor1_user = User(
        full_name="Dr. Priya Mehta",
        email="priya@medicore.com",
        password_hash=hash_password("password123"),
        role="doctor",
        phone="+91 98765 11111"
    )

    doctor2_user = User(
        full_name="Dr. Arjun Rao",
        email="arjun@medicore.com",
        password_hash=hash_password("password123"),
        role="doctor",
        phone="+91 98765 22222"
    )

    doctor3_user = User(
        full_name="Dr. Kavita Nair",
        email="kavita@medicore.com",
        password_hash=hash_password("password123"),
        role="doctor",
        phone="+91 98765 33333"
    )

    lab_user = User(
        full_name="Neha Singh",
        email="neha@medicore.com",
        password_hash=hash_password("password123"),
        role="lab_tech",
        phone="+91 98765 44444"
    )

    admin_user = User(
        full_name="System Admin",
        email="admin@medicore.com",
        password_hash=hash_password("password123"),
        role="admin",
        phone="+91 98765 00000"
    )

    db.add_all([patient_user, doctor1_user, doctor2_user, doctor3_user, lab_user, admin_user])
    db.commit()
    print(f"  ✓ Created {db.query(User).count()} users")

    # ── Patient Profile ───────────────────────
    patient = Patient(
        user_id=patient_user.id,
        dob=date(1984, 3, 15),
        gender="Male",
        blood_group="B+",
        allergies=["Sulfa drugs", "Shellfish"],
        chronic_conditions=["Type 2 Diabetes", "Hypertension"],
        emergency_contact={"name": "Sunita Sharma", "phone": "+91 98765 99999", "relation": "Wife"}
    )
    db.add(patient)
    db.commit()
    print(f"  ✓ Created patient profile: {patient_user.full_name}")

    # ── Provider Profiles ─────────────────────
    provider1 = Provider(
        user_id=doctor1_user.id,
        specialty="Endocrinology",
        hospital="Apollo Hospital, Mumbai",
        license_number="MH-DOC-12345"
    )
    provider2 = Provider(
        user_id=doctor2_user.id,
        specialty="General Medicine",
        hospital="Fortis Hospital, Mumbai",
        license_number="MH-DOC-67890"
    )
    provider3 = Provider(
        user_id=doctor3_user.id,
        specialty="Cardiology",
        hospital="Nanavati Hospital, Mumbai",
        license_number="MH-DOC-11111"
    )
    lab_provider = Provider(
        user_id=lab_user.id,
        specialty="Pathology",
        hospital="SRL Diagnostics",
        license_number="MH-LAB-55555"
    )
    db.add_all([provider1, provider2, provider3, lab_provider])
    db.commit()
    print(f"  ✓ Created {db.query(Provider).count()} provider profiles")

    # ── Consents ──────────────────────────────
    consent1 = Consent(
        patient_id=patient.id,
        provider_id=provider1.id,
        access_level="full",
        status="approved",
        reason="Ongoing diabetes management",
        granted_at=datetime(2026, 1, 15),
        expires_at=datetime(2027, 1, 15)
    )
    consent2 = Consent(
        patient_id=patient.id,
        provider_id=provider2.id,
        access_level="view_only",
        status="approved",
        reason="General checkup referral",
        granted_at=datetime(2026, 3, 1),
        expires_at=datetime(2026, 9, 1)
    )
    consent3 = Consent(
        patient_id=patient.id,
        provider_id=provider3.id,
        access_level="full",
        status="pending",
        reason="Cardiac evaluation referral"
    )
    db.add_all([consent1, consent2, consent3])
    db.commit()
    print("  ✓ Created 3 consents (2 approved, 1 pending)")

    # ── Vitals ────────────────────────────────
    vitals_data = [
        {"bp_systolic": 138, "bp_diastolic": 88, "heart_rate": 78, "blood_sugar": 145.0, "temperature": 98.4, "weight": 82.0, "height": 175.0, "spo2": 97.0, "recorded_at": datetime(2026, 3, 15)},
        {"bp_systolic": 132, "bp_diastolic": 84, "heart_rate": 74, "blood_sugar": 130.0, "temperature": 98.6, "weight": 81.5, "spo2": 98.0, "recorded_at": datetime(2026, 3, 28)},
        {"bp_systolic": 128, "bp_diastolic": 82, "heart_rate": 72, "blood_sugar": 118.0, "temperature": 98.2, "weight": 81.0, "spo2": 98.0, "recorded_at": datetime(2026, 4, 5)},
    ]
    for vd in vitals_data:
        vital = Vital(patient_id=patient.id, recorded_by=doctor1_user.id, **vd)
        db.add(vital)
    db.commit()
    print(f"  ✓ Created {len(vitals_data)} vitals records")

    # ── Prescriptions ─────────────────────────
    rx_data = [
        {"drug_name": "Metformin", "dosage": "500mg", "frequency": "Twice daily (BD)", "duration": "Ongoing", "instructions": "Take after meals", "status": "active"},
        {"drug_name": "Amlodipine", "dosage": "5mg", "frequency": "Once daily (OD)", "duration": "Ongoing", "instructions": "Take in the morning", "status": "active"},
        {"drug_name": "Aspirin", "dosage": "75mg", "frequency": "Once daily (OD)", "duration": "Ongoing", "instructions": "Take after lunch", "status": "active"},
    ]
    for rxd in rx_data:
        rx = Prescription(patient_id=patient.id, doctor_id=provider1.id, **rxd)
        db.add(rx)
    db.commit()
    print(f"  ✓ Created {len(rx_data)} prescriptions")

    # ── Medical Records ───────────────────────
    records_data = [
        {"record_type": "diagnosis", "title": "Type 2 Diabetes Mellitus", "icd10_code": "E11.9", "notes": "Diagnosed in 2020. Currently managed with Metformin. HbA1c trending downward."},
        {"record_type": "diagnosis", "title": "Essential Hypertension", "icd10_code": "I10", "notes": "Diagnosed in 2021. Controlled with Amlodipine 5mg OD."},
        {"record_type": "note", "title": "Follow-up Consultation", "notes": "Patient reports improved blood sugar control. Advised to continue current medication. Next HbA1c in 3 months."},
        {"record_type": "procedure", "title": "Annual Physical Examination", "notes": "Complete physical exam performed. No significant abnormalities found. Continue current management plan."},
    ]
    for rd in records_data:
        record = MedicalRecord(patient_id=patient.id, provider_id=provider1.id, **rd)
        db.add(record)
    db.commit()
    print(f"  ✓ Created {len(records_data)} medical records")

    # ── Lab Reports ───────────────────────────
    # HbA1c Report
    hba1c_report = LabReport(
        patient_id=patient.id,
        uploaded_by=lab_user.id,
        test_name="HbA1c (Glycated Hemoglobin)",
        lab_name="SRL Diagnostics",
        result_summary="HbA1c at 6.8% — good glycemic control",
        status="completed",
        report_date=date(2026, 3, 20)
    )
    db.add(hba1c_report)
    db.commit()

    hba1c_values = [
        LabResultValue(report_id=hba1c_report.id, parameter_name="HbA1c", value="6.8", unit="%", reference_range="4.0 - 5.6", is_abnormal=True),
        LabResultValue(report_id=hba1c_report.id, parameter_name="Estimated Average Glucose", value="148", unit="mg/dL", reference_range="70 - 126", is_abnormal=True),
    ]
    db.add_all(hba1c_values)

    # Lipid Panel Report
    lipid_report = LabReport(
        patient_id=patient.id,
        uploaded_by=lab_user.id,
        test_name="Lipid Panel",
        lab_name="SRL Diagnostics",
        result_summary="All lipid values within normal range",
        status="completed",
        report_date=date(2026, 3, 20)
    )
    db.add(lipid_report)
    db.commit()

    lipid_values = [
        LabResultValue(report_id=lipid_report.id, parameter_name="Total Cholesterol", value="185", unit="mg/dL", reference_range="< 200", is_abnormal=False),
        LabResultValue(report_id=lipid_report.id, parameter_name="LDL Cholesterol", value="110", unit="mg/dL", reference_range="< 130", is_abnormal=False),
        LabResultValue(report_id=lipid_report.id, parameter_name="HDL Cholesterol", value="52", unit="mg/dL", reference_range="> 40", is_abnormal=False),
        LabResultValue(report_id=lipid_report.id, parameter_name="Triglycerides", value="140", unit="mg/dL", reference_range="< 150", is_abnormal=False),
    ]
    db.add_all(lipid_values)

    # CBC Report
    cbc_report = LabReport(
        patient_id=patient.id,
        uploaded_by=lab_user.id,
        test_name="Complete Blood Count (CBC)",
        lab_name="SRL Diagnostics",
        result_summary="CBC within normal limits",
        status="completed",
        report_date=date(2026, 3, 20)
    )
    db.add(cbc_report)
    db.commit()

    cbc_values = [
        LabResultValue(report_id=cbc_report.id, parameter_name="Hemoglobin", value="14.2", unit="g/dL", reference_range="13.5 - 17.5", is_abnormal=False),
        LabResultValue(report_id=cbc_report.id, parameter_name="WBC Count", value="7200", unit="/μL", reference_range="4000 - 11000", is_abnormal=False),
        LabResultValue(report_id=cbc_report.id, parameter_name="Platelet Count", value="245000", unit="/μL", reference_range="150000 - 400000", is_abnormal=False),
        LabResultValue(report_id=cbc_report.id, parameter_name="RBC Count", value="5.1", unit="M/μL", reference_range="4.5 - 5.5", is_abnormal=False),
    ]
    db.add_all(cbc_values)
    db.commit()
    print(f"  ✓ Created 3 lab reports with result values")

    # ── Appointments ──────────────────────────
    appt_data = [
        {"provider_id": provider1.id, "appointment_type": "video", "scheduled_at": datetime(2026, 4, 10, 10, 0), "duration_minutes": 30, "status": "scheduled", "notes": "Follow-up for diabetes management", "meet_link": "https://meet.google.com/abc-defg-hij"},
        {"provider_id": provider2.id, "appointment_type": "in_person", "scheduled_at": datetime(2026, 4, 15, 14, 30), "duration_minutes": 45, "status": "scheduled", "notes": "General checkup"},
        {"provider_id": lab_provider.id, "appointment_type": "lab", "scheduled_at": datetime(2026, 4, 22, 8, 0), "duration_minutes": 15, "status": "scheduled", "notes": "Quarterly blood work - HbA1c, Lipid Panel"},
    ]
    for ad in appt_data:
        appt = Appointment(patient_id=patient.id, **ad)
        db.add(appt)
    db.commit()
    print(f"  ✓ Created {len(appt_data)} appointments")

    # ── Notifications ─────────────────────────
    notifications = [
        Notification(user_id=patient_user.id, type="consent_request", title="New Consent Request", body="Dr. Kavita Nair is requesting full access to your records for cardiac evaluation.", is_read=False),
        Notification(user_id=patient_user.id, type="appointment_reminder", title="Upcoming Appointment", body="Video consultation with Dr. Priya Mehta on Apr 10 at 10:00 AM.", is_read=False),
        Notification(user_id=patient_user.id, type="lab_result", title="Lab Results Available", body="Your HbA1c and Lipid Panel results are ready to view.", is_read=True),
    ]
    db.add_all(notifications)
    db.commit()
    print(f"  ✓ Created {len(notifications)} notifications")

    print("\n✅ Seed complete!")
    print("\n  Login credentials (all passwords: password123):")
    print("  ─────────────────────────────────────────────")
    print("  Patient   : rahul@medicore.com")
    print("  Doctor 1  : priya@medicore.com")
    print("  Doctor 2  : arjun@medicore.com")
    print("  Doctor 3  : kavita@medicore.com")
    print("  Lab Tech  : neha@medicore.com")
    print("  Admin     : admin@medicore.com")

except Exception as e:
    print(f"\n❌ Seed failed: {e}")
    db.rollback()
    raise
finally:
    db.close()
