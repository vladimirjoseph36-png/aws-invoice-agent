"""
Tool: send_alert

Notifies the accountant about an anomaly detected during
reconciliation. In production this would use Amazon SES or SNS.
For the demo, we log the alert.
"""

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("invoice-agent.alert")


def send_alert(invoice_id: str, reason: str) -> dict[str, Any]:
    """
    Send an alert to the accountant.

    Args:
        invoice_id: The ID of the problematic invoice.
        reason: A short human-readable explanation.

    Returns:
        A dictionary confirming the alert was sent.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    message = f"[ALERT] Invoice {invoice_id}: {reason}"
    logger.warning(message)

    return {
        "alert_sent": True,
        "invoice_id": invoice_id,
        "reason": reason,
        "timestamp": timestamp,
        "channel": "log (demo)",
    }