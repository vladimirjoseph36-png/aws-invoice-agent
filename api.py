"""
FastAPI wrapper for the Invoice Reconciliation Agent.

Exposes the Strands agent via a simple REST API so it can be
deployed and tested by the judges.

Endpoints:
    - GET  /             : health check
    - POST /reconcile    : run the agent on an invoice text

Author:
    Anio Joseph

Project:
    AWS Agents for Humans Hackathon 2026
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from main import build_agent


# ----------------------------------------------------------------------
# App
# ----------------------------------------------------------------------

app = FastAPI(
    title="Invoice Reconciliation Agent",
    description="Autonomous AI agent built with Amazon Bedrock + Strands Agents SDK.",
    version="1.0.0",
)

# Build the agent once at startup (reused across requests)
_agent = None


def get_agent():
    """Lazily build and cache the agent."""
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


# ----------------------------------------------------------------------
# Schemas
# ----------------------------------------------------------------------

class ReconcileRequest(BaseModel):
    """Request body for /reconcile."""
    invoice_text: str


class ReconcileResponse(BaseModel):
    """Response body for /reconcile."""
    result: str


# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------

@app.get("/")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "invoice-reconciliation-agent",
        "author": "Anio Joseph",
    }


@app.post("/reconcile", response_model=ReconcileResponse)
def reconcile(request: ReconcileRequest):
    """
    Reconcile an invoice against its purchase order.

    The agent will:
        1. Extract structured data from the invoice
        2. Find the matching purchase order
        3. Compare amounts and detect anomalies
        4. Approve the invoice or send an alert
    """
    if not request.invoice_text.strip():
        raise HTTPException(status_code=400, detail="invoice_text cannot be empty")

    try:
        agent = get_agent()
        response = agent(request.invoice_text)
        return ReconcileResponse(result=str(response))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))