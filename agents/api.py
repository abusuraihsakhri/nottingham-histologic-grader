"""
FastAPI REST API Server for Nottingham Histologic Grader.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import Field
from nottingham_grader import calculate_metrics
from .base import SecurityException
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Nottingham Histologic Grader API",
    description="Nottingham grade calculator plus legacy demonstration audit API (not clinical decision support)",
    version="3.1.0",
)


class GradeRequest(BaseModel):
    v1: int = Field(strict=True, ge=1, le=3, description="Tubule formation score")
    v2: int = Field(strict=True, ge=1, le=3, description="Nuclear pleomorphism score")
    v3: int = Field(strict=True, ge=1, le=3, description="Calibrated mitotic component score")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(Path(__file__).resolve().parent.parent / "web" / "index.html")


@app.post("/api/grade")
def api_grade(payload: GradeRequest):
    return calculate_metrics(**payload.model_dump())


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "nottingham-histologic-grader", "grading": "Nottingham (Elston-Ellis)", "legacy_audit": "demonstration only"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
        return dossier.to_dict()
    except SecurityException:
        raise HTTPException(status_code=422, detail="Sensitive identifier detected") from None


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=422, detail="Sensitive identifier detected") from None


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}


# Keep the demonstration API routes above this static fallback.
app.mount("/", StaticFiles(directory=Path(__file__).resolve().parent.parent / "web", html=True), name="web")
