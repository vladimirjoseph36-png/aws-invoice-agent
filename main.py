"""
Invoice Reconciliation Agent — Main entry point.

This agent autonomously reconciles supplier invoices against
purchase orders (POs), detects anomalies, and notifies the accountant.

Built with:
    - Strands Agents SDK (AWS)
    - Amazon Bedrock (Claude Sonnet 4.6)

Author:
    Anio Joseph

Project:
    AWS Agents for Humans Hackathon 2026
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
from utils.style import banner, section, ok, info, Colors


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
        "AWS Agents for Humans Hackathon 2026  —  by Anio Joseph",
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