# ──────────────────────────────────────────────
# main.py — FastAPI application entry point
# Mounts all routers, CORS middleware, static uploads
# ──────────────────────────────────────────────

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from config import settings
from database import engine, Base
from middleware.audit import AuditMiddleware

# Import all route modules
from routes import auth, patients, records, vitals, prescriptions, labs, consents, appointments, admin

# ── Validate production secrets at startup ─────
settings.validate_production()

# ── Create tables ─────────────────────────────
Base.metadata.create_all(bind=engine)

# ── FastAPI app ───────────────────────────────
# Disable interactive docs in production (no /docs or /redoc exposure)
app = FastAPI(
    title="MediCore — Patient-Centric EHR",
    description="Clinical Data Management platform where the patient owns and controls their health data.",
    version="1.0.0",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
)

# ── CORS — locked to env-configured origins ────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


# ── Audit middleware — log every API call ──────
app.add_middleware(AuditMiddleware)

# ── Static file serving for uploads ────────────
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ── Include all routers ───────────────────────
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(records.router)
app.include_router(vitals.router)
app.include_router(prescriptions.router)
app.include_router(labs.router)
app.include_router(consents.router)
app.include_router(appointments.router)
app.include_router(admin.router)


# ── Root endpoint — redirect to login ─────────
@app.get("/")
def root():
    return RedirectResponse(url="/app/index.html")

# ── Serve frontend static files (MUST be last) ─
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

