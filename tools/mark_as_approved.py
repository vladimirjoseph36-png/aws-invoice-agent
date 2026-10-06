"""
Tool: mark_as_approved

Marks an invoice as approved after successful reconciliation.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from strands import tool

logger = logging.getLogger("invoice-agent.approval")

_APPROVED_INVOICES: list[dict[str, Any]] = []


@tool
def mark_as_approved(invoice_id: str) -> dict[str, Any]:
    """
    Mark an invoice as approved.

    Use this tool ONLY when compare_amounts confirms the invoice
    matches the PO with no anomalies.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    record = {"invoice_id": invoice_id, "approved_at": timestamp}
    _APPROVED_INVOICES.append(record)

    logger.info("Invoice %s marked as APPROVED at %s", invoice_id, timestamp)

    return {
        "approved": True,
        "invoice_id": invoice_id,
        "approved_at": timestamp,
        "total_approved": len(_APPROVED_INVOICES),
    }
