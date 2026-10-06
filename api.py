"""
FastAPI wrapper for the Invoice Reconciliation Agent.

Exposes the Strands agent via:
    - A REST API (for judges / integrations)
    - A simulated Alexa+ web interface (for the demo video)

Endpoints:
    - GET  /                 : health check
    - GET  /alexa            : Alexa+ simulated chat UI
    - POST /reconcile        : run the agent on an invoice text
    - POST /simulate-alexa   : run the agent from the Alexa+ chat UI

Author:
    Anio Joseph

Project:
    Build, Ship, Shape — Amazon Developer Hackathon 2026
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from main import build_agent


# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


# ----------------------------------------------------------------------
# App
# ----------------------------------------------------------------------

app = FastAPI(
    title="Invoice Reconciliation Agent",
    description=(
        "Autonomous AI agent built with Amazon Bedrock + Strands Agents SDK. "
        "Includes a simulated Alexa+ interface."
    ),
    version="1.0.0",
)

# Serve static files (CSS, JS)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ----------------------------------------------------------------------
# Agent (built once, reused across requests)
# ----------------------------------------------------------------------

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


class AlexaRequest(BaseModel):
    """Request body for /simulate-alexa."""
    message: str


class AlexaResponse(BaseModel):
    """Response body for /simulate-alexa."""
    reply: str


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
        "endpoints": {
            "alexa_ui": "/alexa",
            "reconcile": "POST /reconcile",
            "simulate_alexa": "POST /simulate-alexa",
        },
    }


@app.get("/alexa", response_class=HTMLResponse)
def alexa_ui():
    """Serve the simulated Alexa+ chat interface."""
    template_path = TEMPLATES_DIR / "alexa.html"
    if not template_path.exists():
        raise HTTPException(status_code=500, detail="Template alexa.html not found")
    return HTMLResponse(content=template_path.read_text(encoding="utf-8"))


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


@app.post("/simulate-alexa", response_model=AlexaResponse)
def simulate_alexa(request: AlexaRequest):
    """
    Simulate an Alexa+ interaction.

    Receives a natural-language command from the chat UI, forwards it
    to the Strands agent, and returns the agent's reply.
    """
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="message cannot be empty")

    # Strip the "Alexa, " wake word if present
    for prefix in ("alexa,", "alexa "):
        if message.lower().startswith(prefix):
            message = message[len(prefix):].strip()
            break

    try:
        agent = get_agent()
        response = agent(message)
        return AlexaResponse(reply=str(response))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))