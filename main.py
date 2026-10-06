"""
Invoice Reconciliation Agent — Main entry point.

This agent autonomously reconciles supplier invoices against
purchase orders (POs), detects anomalies, and notifies the accountant.

The agent is robust to a wide range of inputs:
    - Complete invoices (full workflow)
    - Incomplete invoices (asks for missing fields)
    - Demo invoice IDs (uses pre-loaded data)
    - Off-topic messages (politely redirects)
    - Ambiguous input (asks for clarification)

Built with:
    - Strands Agents SDK (AWS)
    - Amazon Bedrock (Claude Sonnet 4.6)

Author:
    Anio Joseph

Project:
    Build, Ship, Shape — Amazon Developer Hackathon 2026
"""

import logging
import os
import sys

# ----------------------------------------------------------------------
# Load environment variables FIRST (before any AWS import)
# ----------------------------------------------------------------------
from dotenv import load_dotenv

load_dotenv()

# Now AWS credentials are available to boto3
from strands import Agent
from strands.models import BedrockModel

from tools.extract_invoice import extract_invoice
from tools.find_purchase_order import find_purchase_order
from tools.compare_amounts import compare_amounts
from tools.send_alert import send_alert
from tools.mark_as_approved import mark_as_approved
from utils.style import banner, section, ok, Colors


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
# System prompt (robust, handles all input types)
# ----------------------------------------------------------------------

SYSTEM_PROMPT = """You are an autonomous Invoice Reconciliation Agent.

Your job is to help accountants reconcile supplier invoices against
purchase orders (POs).

You have access to the following tools:
    - extract_invoice: extract structured data from an invoice text
    - find_purchase_order: find the matching PO in the database
    - compare_amounts: compare the invoice with the PO and detect anomalies
    - send_alert: notify the accountant if there's a problem
    - mark_as_approved: mark the invoice as approved if everything matches

================================================================
HOW TO HANDLE INPUTS — READ CAREFULLY
================================================================

A valid invoice MUST contain at least:
    - Invoice ID       (e.g. "Invoice #INV-2026-0042")
    - Supplier name    (e.g. "Acme Supplies Ltd.")
    - PO Reference     (e.g. "PO-2026-0117")
    - Amount in USD    (e.g. "$1,250.00")
    - VAT              (e.g. "$250.00")

CASE 1 — COMPLETE invoice (all 5 fields present):
    → Follow the WORKFLOW below (extract → find PO → compare → approve/alert).

CASE 2 — INCOMPLETE invoice (one or more fields missing):
    → Do NOT call any tool.
    → Politely list the missing fields and ask the user to provide them.
    → Example: "I can help, but I still need the following fields:
      PO Reference, Amount, VAT. Please provide them."

CASE 3 — The user mentions ONLY the invoice ID "INV-2026-0042":
    → Use the pre-loaded DEMO DATA below and run the full workflow.

CASE 4 — OFF-TOPIC input (greeting, joke, random text, unrelated question):
    → Do NOT call any tool.
    → Politely explain that you are an Invoice Reconciliation Agent.
    → Ask the user to provide a supplier invoice to reconcile.
    → Example: "I'm an invoice reconciliation agent. Please provide a
      supplier invoice (with ID, supplier, PO reference, amount, and VAT)
      and I'll reconcile it for you."

CASE 5 — AMBIGUOUS input (looks like an invoice but unclear):
    → Do NOT call any tool.
    → Ask for clarification and show a concrete example.

NEVER call a tool if the input is not a valid invoice.
NEVER invent data.
NEVER answer questions that are unrelated to invoice reconciliation.
ALWAYS reply in the same language as the user (English, French, or Spanish).

================================================================
WORKFLOW (only for valid invoices)
================================================================

1. Call extract_invoice FIRST to get the structured data.
2. Call find_purchase_order to locate the matching PO.
3. Call compare_amounts to verify the invoice matches the PO.
4. If there are anomalies:
   - Call send_alert with a clear explanation.
   - Do NOT mark the invoice as approved.
5. If everything matches:
   - Call mark_as_approved with the invoice ID.
   - Confirm the approval in your final response.

================================================================
DEMO DATA
================================================================

If the user mentions the invoice ID "INV-2026-0042" without providing
the full text, use this sample invoice content:

Invoice #INV-2026-0042
Supplier: Acme Supplies Ltd.
PO Reference: PO-2026-0117
Amount: $1,250.00
VAT: $250.00
Items: 5x Widget A, 2x Widget B

================================================================

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
    region = os.getenv("AWS_REGION", "us-east-1")
    model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-sonnet-4-6")

    logger.info("Using Bedrock model: %s (region: %s)", model_id, region)

    model = BedrockModel(
        model_id=model_id,
        region_name=region,
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
    # --- Banner ---
    print()
    print(banner(
        "Invoice Reconciliation Agent",
        "Build, Ship, Shape — Amazon Developer Hackathon 2026  —  by Anio Joseph",
    ))
    print()

    # --- Build the agent ---
    logger.info("Building Invoice Reconciliation Agent...")
    agent = build_agent()

    # --- Invoice to process ---
    sample_invoice = (
        "Please reconcile this invoice:\n"
        "Invoice #INV-2026-0042\n"
        "Supplier: Acme Supplies Ltd.\n"
        "PO Reference: PO-2026-0117\n"
        "Amount: $1,250.00\n"
        "VAT: $250.00\n"
        "Items: 5x Widget A, 2x Widget B\n"
    )

    print(section("Processing invoice INV-2026-0042"))
    print(f"  {Colors.DIM}Supplier : Acme Supplies Ltd.{Colors.RESET}")
    print(f"  {Colors.DIM}Amount   : $1,250.00{Colors.RESET}")
    print(f"  {Colors.DIM}VAT      : $250.00{Colors.RESET}")
    print(f"  {Colors.DIM}PO Ref   : PO-2026-0117{Colors.RESET}")
    print()

    # --- Run the agent ---
    logger.info("Sending invoice to agent...")
    response = agent(sample_invoice)

    # --- Final summary ---
    print()
    print(section("Final report"))
    print()
    print(response)
    print()
    print(ok("Reconciliation complete."))
    print()


if __name__ == "__main__":
    main()