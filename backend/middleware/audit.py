# ──────────────────────────────────────────────
# middleware/audit.py — Audit logging middleware
# Logs every API request to the audit_logs table
# ──────────────────────────────────────────────

from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from database import SessionLocal
from models import AuditLog
from auth import decode_token


class AuditMiddleware(BaseHTTPMiddleware):
    """Log every API request to audit_logs for traceability."""

    async def dispatch(self, request: Request, call_next):
        # Process the request
        response = await call_next(request)

        # Only audit API calls (skip static files, docs)
        if not request.url.path.startswith("/api"):
            return response

        # Extract actor info from JWT if present
        actor_id = None
        actor_type = None
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_token(token)
            if payload:
                actor_id = payload.get("sub")
                actor_type = payload.get("role")

        # Determine action from method + path
        action = f"{request.method} {request.url.path}"

        # Get client IP
        ip_address = request.client.host if request.client else None

        # Write audit log entry
        try:
            db = SessionLocal()
            log_entry = AuditLog(
                actor_id=actor_id,
                actor_type=actor_type,
                action=action,
                resource_type=request.url.path.split("/")[2] if len(request.url.path.split("/")) > 2 else None,
                ip_address=ip_address,
                metadata={"status_code": response.status_code, "query": str(request.query_params)},
                created_at=datetime.utcnow()
            )
            db.add(log_entry)
            db.commit()
            db.close()
        except Exception:
            pass  # Don't break the request if audit logging fails

        return response
