"""Annex B personal information bank (PIB) code classifications."""

import re
from typing import Optional


PIB_TYPES = {
    "PPU": "Public Bank",
    "PPE": "Particular Bank",
    "PCE": "Central Bank",
    "PCU": "Public Central Bank",
    "PSE": "Employee Standard Bank",
    "PSU": "Public Standard Bank",
}

PIB_CODE_RE = re.compile(r"\b(" + "|".join(PIB_TYPES) + r")\b", flags=re.IGNORECASE)


def get_pib_code(*bank_numbers: Optional[str]) -> str:
    """Return the first Annex B code found in the supplied bank numbers."""
    for bank_number in bank_numbers:
        if not isinstance(bank_number, str):
            continue
        match = PIB_CODE_RE.search(bank_number)
        if match:
            return match.group(1).upper()
    return ""


def get_pib_type(*bank_numbers: Optional[str]) -> str:
    """Return the Annex B PIB type for the first recognized bank code."""
    return PIB_TYPES.get(get_pib_code(*bank_numbers), "")
