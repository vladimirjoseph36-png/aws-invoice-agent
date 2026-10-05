"""
Tool: mark_as_approved

Marks an invoice as approved after successful reconciliation.
In production this would update a database record.
For the demo, we log the approval and keep an in-memory list.
"""

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("invoice-agent.approval")

_APPROVED_INVOICES: list[dict[str, Any]] = []


def mark_as_approved(invoice_id: str) -> dict[str, Any]:
    """
    Mark an invoice as approved.

    Args:
        invoice_id: The ID of the invoice to approve.

    Returns:
        A dictionary confirming the approval.
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