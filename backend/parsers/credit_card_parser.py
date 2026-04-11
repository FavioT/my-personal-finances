import re
from datetime import date
from fastapi import HTTPException
from parsers.pdf_parser import _is_macro_format, _parse_macro_text, _is_bbva_format, _parse_bbva_text


# Matches dates like DD/MM/YYYY, DD/MM/YY, DD-MM-YYYY, DD-MM-YY
_DATE_RE = re.compile(r"\b(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})\b")
# Matches an amount: optional sign, digits, optional thousands separator (. or ,), decimal part
_AMOUNT_RE = re.compile(r"(-?\$?\s*[\d\.]+,\d{2}|-?\$?\s*[\d,]+\.\d{2}|-?\$?\s*\d+)\s*$")


def _parse_date(day: str, month: str, year: str) -> date | None:
    try:
        d, m, y = int(day), int(month), int(year)
        if y < 100:
            y += 2000
        return date(y, m, d)
    except ValueError:
        return None


def _parse_amount(raw: str) -> float:
    """Parse European-style amounts (1.234,56) and US-style (1,234.56)."""
    s = raw.strip().lstrip("$").replace(" ", "")
    # European format: comma is decimal separator, dot is thousands separator
    # Detected when a comma is followed by exactly two digits at the end
    # AND there is a dot present (acting as thousands separator), e.g. "1.234,56"
    if re.search(r"\.\d{3}", s) and re.search(r",\d{2}$", s):
        s = s.replace(".", "").replace(",", ".")
    else:
        # US format or plain integer: remove thousands commas, keep dot decimal
        s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return 0.0


def parse_credit_card_text(text: str, bank: str) -> list[dict]:
    """Parse plain-text credit card statement (BBVA or Macro format).

    Each non-empty line is examined for a leading date, a trailing amount,
    and everything in between is used as the description.
    Lines that do not match are silently skipped (headers, footers, totals, etc.).
    """
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="The submitted text is empty.")

    # Macro format uses Spanish month names instead of numeric dates
    if bank.lower() == "macro" and _is_macro_format(text):
        transactions = _parse_macro_text(text, source_name=bank.upper(), source_type="credit_card_macro")
        if transactions:
            return transactions

    # BBVA format uses DD-MonthAbbr-YY with 6-digit coupon numbers
    if bank.lower() in ("bbva", "bbva_visa", "bbva_mastercard") and _is_bbva_format(text):
        source_type_val = f"credit_card_{bank.lower()}"
        transactions = _parse_bbva_text(text, source_name=bank.upper(), source_type=source_type_val)
        if transactions:
            return transactions

    source_type = f"credit_card_{bank.lower()}"
    transactions: list[dict] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        date_match = _DATE_RE.search(line)
        if not date_match:
            continue

        parsed_date = _parse_date(date_match.group(1), date_match.group(2), date_match.group(3))
        if parsed_date is None:
            continue

        # Everything after the date is candidate for "description + amount"
        after_date = line[date_match.end():].strip()
        if not after_date:
            continue

        amount_match = _AMOUNT_RE.search(after_date)
        if not amount_match:
            continue

        amount = _parse_amount(amount_match.group(0))
        description = after_date[: amount_match.start()].strip(" \t-|")
        if not description:
            continue

        transactions.append(
            {
                "date": parsed_date,
                "description": description,
                "amount": amount,
                "source": bank.upper(),
                "source_type": source_type,
            }
        )

    if not transactions:
        raise HTTPException(
            status_code=400,
            detail=(
                "No transactions could be parsed from the submitted text. "
                "Make sure each line contains a date (DD/MM/YYYY), a description, and an amount."
            ),
        )

    return transactions
