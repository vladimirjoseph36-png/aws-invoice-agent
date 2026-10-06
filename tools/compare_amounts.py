"""
Tool: compare_amounts

Compares an invoice against its matching purchase order and
returns a list of anomalies (or an empty list if everything matches).
"""

from typing import Any

from strands import tool


@tool
def compare_amounts(
    invoice_amount: float,
    invoice_vat: float,
    po_amount: float,
    po_vat: float,
) -> dict[str, Any]:
    """
    Compare invoice amounts with PO amounts and detect anomalies.

    Use this tool AFTER finding the PO to verify the invoice matches.
    """
    anomalies: list[dict[str, Any]] = []

    amount_diff = round(invoice_amount - po_amount, 2)
    vat_diff = round(invoice_vat - po_vat, 2)

    if abs(amount_diff) > 0.01:
        anomalies.append({
            "type": "amount_mismatch",
            "invoice": invoice_amount,
            "po": po_amount,
            "difference": amount_diff,
        })

    if abs(vat_diff) > 0.01:
        anomalies.append({
            "type": "vat_mismatch",
            "invoice": invoice_vat,
            "po": po_vat,
            "difference": vat_diff,
        })

    return {
        "matches": len(anomalies) == 0,
        "anomalies": anomalies,
    }
