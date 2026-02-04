# iam_core/api/decision_trace.py
from fastapi import APIRouter
from fastapi import APIRouter
from iam_core.audit.attack_trace_store import get_trace

router = APIRouter()

@router.get("/api/decision/{session_id}")
def decision_trace(session_id: str):
    return get_trace(session_id) or {}

