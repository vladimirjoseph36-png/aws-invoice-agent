"""
Terminal styling helpers (colors, banners, formatting).

Uses ANSI escape codes — works on Windows 10+, macOS, and Linux.
No external dependency required.

Author:
    Anio Joseph

Project:
    AWS Agents for Humans Hackathon 2026
"""

import os
import sys


# ----------------------------------------------------------------------
# ANSI color codes
# ----------------------------------------------------------------------

class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    # Background
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_BLUE = "\033[44m"


def _supports_color() -> bool:
    """Return True if the terminal supports ANSI colors."""
    if os.name == "nt":  # Windows
        # Enable ANSI on Windows 10+
        os.system("")
        return True
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


# Enable colors on Windows automatically when this module is imported
if os.name == "nt":
    os.system("")


def colorize(text: str, color: str) -> str:
    """Wrap text in an ANSI color code."""
    return f"{color}{text}{Colors.RESET}"


def ok(text: str) -> str:
    """Green with a check mark."""
    return colorize(f"✅ {text}", Colors.GREEN)


def error(text: str) -> str:
    """Red with a cross mark."""
    return colorize(f"❌ {text}", Colors.RED)


def warning(text: str) -> str:
    """Yellow with a warning sign."""
    return colorize(f"⚠️  {text}", Colors.YELLOW)


def info(text: str) -> str:
    """Cyan with an info sign."""
    return colorize(f"ℹ️  {text}", Colors.CYAN)


def banner(title: str, subtitle: str = "") -> str:
    """
    Return an ASCII banner with the given title and subtitle.

    Args:
        title: The main title.
        subtitle: Optional subtitle shown below the title.

    Returns:
        A multi-line string with the banner.
    """
    width = 68
    top = "═" * width
    middle = f"  {title}"

    lines = [
        f"{Colors.CYAN}╔{top}╗{Colors.RESET}",
        f"{Colors.CYAN}║{Colors.RESET}{Colors.BOLD}{middle:<{width}}{Colors.RESET}{Colors.CYAN}║{Colors.RESET}",
    ]

    if subtitle:
        sub = f"  {subtitle}"
        lines.append(
            f"{Colors.CYAN}║{Colors.RESET}{Colors.DIM}{sub:<{width}}{Colors.RESET}{Colors.CYAN}║{Colors.RESET}"
        )

    lines.append(f"{Colors.CYAN}╚{top}╝{Colors.RESET}")
    return "\n".join(lines)


def section(title: str) -> str:
    """A section divider with a title."""
    return f"\n{Colors.BOLD}{Colors.BLUE}▶ {title}{Colors.RESET}"


def step(number: int, total: int, description: str) -> str:
    """A formatted step line (e.g. 'Step 1/4 — Extracting invoice')."""
    return (
        f"{Colors.MAGENTA}[{number}/{total}]{Colors.RESET} "
        f"{Colors.BOLD}{description}{Colors.RESET}"
    )


def table_row(label: str, value: str, matched: bool = True) -> str:
    """A single row formatted like a table with a ✅/❌ status."""
    status = "✅" if matched else "❌"
    label_padded = f"{label:<20}"
    value_padded = f"{value:<30}"
    return f"  {status}  {label_padded} {value_padded}"