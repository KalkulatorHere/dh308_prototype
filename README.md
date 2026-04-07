# MediCore

**A Patient-Centric Clinical Data Management (CDM) Platform**

MediCore is a full-stack, role-based Electronic Health Record (EHR) system that places data ownership squarely in the hands of the patient. It features a complete **FastAPI backend** (SQLite, SQLAlchemy, JWT Authentication) and a scalable **Vanilla HTML/Tailwind/AlpineJS frontend**.

## 🌟 Key Features

*   **Role-Based Access Control:** Separate, optimized interfaces for Patients, Doctors, Lab Technicians, and Administrators.
*   **Consent-Gated Data (ABAC):** Doctors cannot view patient records without explicit, active consent granted by the patient.
*   **Comprehensive Audit Logging:** Every read/write action on sensitive medical data is logged tracking the actor, action, and resource.
*   **"No-Build" Frontend:** Fast, beginner-friendly frontend using CDN-delivered Tailwind CSS, Alpine.js, and Lucide icons.
*   **JWT Authentication:** Secure, stateless sessions spanning both Python APIs and JavaScript clients.

## 🛠 Tech Stack

### Backend
*   **Framework:** FastAPI
*   **Database:** SQLite + SQLAlchemy ORM (12 interconnected tables)
*   **Authentication:** JWT (JSON Web Tokens) with `python-jose`, passwords hashed via `bcrypt`
*   **Validation:** Pydantic Models

### Frontend
*   **Structure:** Vanilla HTML5 + JavaScript
*   **Styling:** Tailwind CSS (via CDN) with custom Glassmorphism aesthetics
*   **Reactivity:** Alpine.js (via CDN)
*   **Icons & Charts:** Lucide Icons, Chart.js

## 📁 Repository Structure

```
MediCore/
├── backend/
│   ├── main.py              # FastAPI entry point & config
│   ├── database.py          # SQLite engine & DeclarativeBase
│   ├── models.py            # 12 SQLAlchemy tables (Users, Records, Consents, etc.)
│   ├── schemas.py           # Pydantic schemas (In/Out)
│   ├── auth.py              # JWT generation/decoding, bcrypt
│   ├── dependencies.py      # Auth guards (get_current_user, require_role)
│   ├── seed.py              # Demo user/data seeder (cleans & populates DB)
│   ├── requirements.txt     # Python dependencies
│   ├── middleware/          # Audit & Consent middleware
│   └── routes/              # Modular API endpoints (auth, patients, vitals, etc.)
│
└── frontend/                # (Served by FastAPI at /app/)
    ├── index.html           # Universal login & registration page
    ├── shared/              # api.js, auth.js, components.js (Shared logic)
    ├── patient/             # Dashboard, Timeline, Labs, Consent Manager, Profile, etc.
    ├── doctor/              # Dashboard, Patient Viewer, Prescriptions, Clinical Notes
    ├── lab/                 # Report Uploader, Queue Viewer
    └── admin/               # System stats, Audit viewer, User management
```

## 🚀 Quick Start Guide

### 1. Requirements
*   Python 3.10+

### 2. Setup Backend & Install Dependencies
Open your terminal and navigate to the backend folder:
```bash
cd backend
pip install -r requirements.txt
```

### 3. Seed the Database
MediCore comes with a seeder script that populates realistic demo data (patients, doctors, medical records, etc.) instantly.
```bash
python seed.py
```

### 4. Run the Server
Start the FastAPI server. It mounts the API at `/api` and the frontend at `/app`.
```bash
python -m uvicorn main:app --reload --port 8000
```
> *(The `-m` flag is recommended on Windows to avoid path issues)*

### 5. Log In
Open your browser and navigate to: **http://127.0.0.1:8000**
You will be redirected to the login page. Use the "Quick Login" buttons at the bottom of the form, or use the following demo accounts:

| Role | Email Login | Password |
| :--- | :--- | :--- |
| **Patient** | `rahul@medicore.com` | `password123` |
| **Doctor** | `priya@medicore.com` | `password123` |
| **Lab Tech** | `neha@medicore.com` | `password123` |
| **Admin** | `admin@medicore.com` | `password123` |

## 🔒 Security Posture

MediCore employs several layers of security:
1.  **Authentication (`auth.py`)**: Passwords are not stored in plaintext; they are hashed using `bcrypt`. Sessions rely on short-lived JWT Access Tokens and Refresh Tokens.
2.  **Authorization (`dependencies.py`)**: Critical endpoints enforce `require_role(["doctor", "admin"])` checks before fulfilling requests.
3.  **Consent Middleware (`middleware/consent_check.py`)**: When a doctor requests a patient's records, this dependency queries the `consents` table to verify an active, non-expired, and approved mandate exists.
4.  **Audit Middleware (`middleware/audit.py`)**: Transparently logs API calls matching critical patterns (e.g., viewing records) directly into the `audit_logs` table for future inspection by administrators.

## 🎨 UI/UX Design

The application uses a distinctive **Dark Glassmorphism** theme to minimize eye strain in clinical environments while looking thoroughly modern.
*   **Base Color:** Deep Navy (`#0B0F1A`)
*   **Cards:** Translucent surfaces (`#131c2e` with `0.08` opacity borders)
*   **Accents:** Teal (`#00d4aa`), Purple, Blue, Amber.
*   **Layout:** Responsive fixed-sidebar layout (desktop-first) ensuring critical navigation is always available.
