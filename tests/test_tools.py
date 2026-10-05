"""
Unit tests for the Invoice Reconciliation Agent tools.

Run with:
    python -m pytest tests/ -v
or:
    python tests/test_tools.py
"""

from tools.extract_invoice import extract_invoice
from tools.find_purchase_order import find_purchase_order
from tools.compare_amounts import compare_amounts
from tools.send_alert import send_alert
from tools.mark_as_approved import mark_as_approved


# Sample invoice text used by several tests
SAMPLE_INVOICE = (
    "Invoice #INV-2026-0042\n"
    "Supplier: Acme Supplies Ltd.\n"
    "PO Reference: PO-2026-0117\n"
    "Amount: $1,250.00\n"
    "VAT: $250.00\n"
    "Items: 5x Widget A, 2x Widget B\n"
)


def test_extract_invoice() -> None:
    """extract_invoice should parse all key fields."""
    result = extract_invoice(SAMPLE_INVOICE)

    assert result["invoice_id"] == "INV-2026-0042"
    assert result["supplier"] == "Acme Supplies Ltd."
    assert result["po_reference"] == "PO-2026-0117"
    assert result["amount"] == 1250.00
    assert result["vat"] == 250.00

    print("✅ test_extract_invoice passed")


def test_find_purchase_order_exists() -> None:
    """find_purchase_order should return the PO when it exists."""
    result = find_purchase_order("PO-2026-0117")

    assert result["found"] is True
    assert result["po_reference"] == "PO-2026-0117"
    assert result["amount"] == 1250.00
    assert result["supplier"] == "Acme Supplies Ltd."

    print("✅ test_find_purchase_order_exists passed")


def test_find_purchase_order_missing() -> None:
    """find_purchase_order should return found=False when missing."""
    result = find_purchase_order("PO-NOT-FOUND")

    assert result["found"] is False
    assert result["po_reference"] == "PO-NOT-FOUND"

    print("✅ test_find_purchase_order_missing passed")


def test_compare_amounts_match() -> None:
    """compare_amounts should report no anomalies when everything matches."""
    result = compare_amounts(
        invoice_amount=1250.00,
        invoice_vat=250.00,
        po_amount=1250.00,
        po_vat=250.00,
    )

    assert result["matches"] is True
    assert result["anomalies"] == []

    print("✅ test_compare_amounts_match passed")


def test_compare_amounts_mismatch() -> None:
    """compare_amounts should detect an amount mismatch."""
    result = compare_amounts(
        invoice_amount=1300.00,
        invoice_vat=250.00,
        po_amount=1250.00,
        po_vat=250.00,
    )

    assert result["matches"] is False
    assert len(result["anomalies"]) == 1
    assert result["anomalies"][0]["type"] == "amount_mismatch"
    assert result["anomalies"][0]["difference"] == 50.00

    print("✅ test_compare_amounts_mismatch passed")


def test_send_alert() -> None:
    """send_alert should return a confirmation dict."""
    result = send_alert(
        invoice_id="INV-2026-0042",
        reason="Amount mismatch: +50.00",
    )

    assert result["alert_sent"] is True
    assert result["invoice_id"] == "INV-2026-0042"
    assert "mismatch" in result["reason"].lower()

    print("✅ test_send_alert passed")


def test_mark_as_approved() -> None:
    """mark_as_approved should return a confirmation dict."""
    result = mark_as_approved("INV-2026-0042")

    assert result["approved"] is True
    assert result["invoice_id"] == "INV-2026-0042"
    assert "approved_at" in result

    print("✅ test_mark_as_approved passed")


# ----------------------------------------------------------------------
# Simple runner (no pytest required)
# ----------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_extract_invoice,
        test_find_purchase_order_exists,
        test_find_purchase_order_missing,
        test_compare_amounts_match,
        test_compare_amounts_mismatch,
        test_send_alert,
        test_mark_as_approved,
    ]

    print("\n🚀 Running tool tests...\n")
    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as exc:
            print(f"❌ {test.__name__} FAILED: {exc}")
            failed += 1

    print(f"\n📊 Results: {passed} passed, {failed} failed")