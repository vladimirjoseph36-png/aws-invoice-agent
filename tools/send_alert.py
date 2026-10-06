"""
Tool: send_alert

Notifies the accountant about an anomaly detected during
reconciliation. In production this would use Amazon SES or SNS.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from strands import tool

logger = logging.getLogger("invoice-agent.alert")


@tool
def send_alert(invoice_id: str, reason: str) -> dict[str, Any]:
    """
    Send an alert to the accountant about a problematic invoice.

    Use this tool when compare_amounts returns anomalies.
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
