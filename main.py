"""
Invoice Reconciliation Agent — Main entry point.

This agent autonomously reconciles supplier invoices against
purchase orders (POs), detects anomalies, and notifies the accountant.

Built with:
    - Strands Agents SDK (AWS)
    - Amazon Bedrock (Claude 3.5 Sonnet)

Author:
    Anio Joseph

Project:
    AWS Agents for Humans Hackathon 2026
"""

import logging
import sys

from strands import Agent
from strands.models import BedrockModel

from tools.extract_invoice import extract_invoice
from tools.find_purchase_order import find_purchase_order
from tools.compare_amounts import compare_amounts
from tools.send_alert import send_alert
from tools.mark_as_approved import mark_as_approved


# ----------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("invoice-agent")


# ----------------------------------------------------------------------
# System prompt
# ----------------------------------------------------------------------

SYSTEM_PROMPT = """You are an autonomous Invoice Reconciliation Agent.

Your job is to help accountants reconcile supplier invoices against
purchase orders (POs).

You have access to the following tools:
    - extract_invoice: extract structured data from an invoice (PDF or text)
    - find_purchase_order: find the matching PO in the database
    - compare_amounts: compare the invoice with the PO and detect anomalies
    - send_alert: notify the accountant if there's a problem
    - mark_as_approved: mark the invoice as approved if everything matches

WORKFLOW — follow these steps exactly:

1. When given an invoice, ALWAYS call extract_invoice FIRST to get its data.
2. Then call find_purchase_order to locate the matching PO.
3. Then call compare_amounts to verify the invoice matches the PO.
4. If there are anomalies (amount mismatch, missing PO, etc.):
   - Call send_alert with a clear explanation of the problem.
   - Do NOT mark the invoice as approved.
5. If everything matches:
   - Call mark_as_approved with the invoice ID.
   - Confirm the approval in your final response.

Always be concise, factual, and professional.
Never invent data that is not returned by the tools."""


# ----------------------------------------------------------------------
# Agent factory
# ----------------------------------------------------------------------

def build_agent() -> Agent:
    """
    Build and return the reconciliation agent.

    Returns:
        A configured :class:`strands.Agent` instance.
    """
    # Bedrock model (Claude 3.5 Sonnet)
    model = BedrockModel(
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        region_name="us-east-1",
    )

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[
            extract_invoice,
            find_purchase_order,
            compare_amounts,
            send_alert,
            mark_as_approved,
        ],
    )
    return agent


# ----------------------------------------------------------------------
# CLI demo
# ----------------------------------------------------------------------

def main() -> None:
    """Run a demo reconciliation on a sample invoice."""
    logger.info("Building Invoice Reconciliation Agent...")
    agent = build_agent()

    sample_invoice = (
        "Please reconcile this invoice:\n"
        "Invoice #INV-2026-0042\n"
        "Supplier: Acme Supplies Ltd.\n"
        "PO Reference: PO-2026-0117\n"
        "Amount: $1,250.00\n"
        "VAT: $250.00\n"
        "Items: 5x Widget A, 2x Widget B\n"
    )

    logger.info("Sending invoice to agent...")
    response = agent(sample_invoice)
    logger.info("Agent response:\n%s", response)


if __name__ == "__main__":
    main()