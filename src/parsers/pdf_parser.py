import re
from datetime import date
from typing import Optional
import pdfplumber
import pandas as pd



# ---------------------------------------------------------------------------
# Macro credit card text-based parser (fixed-width monospace layout)
# ---------------------------------------------------------------------------

_SPANISH_MONTHS = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
}

# Line patterns
_SKIP_RE   = re.compile(r"(TARJETA\s+\d+\s+Total|^\s*$)", re.IGNORECASE)
_DATE_RE   = re.compile(
    r"^\s*(\d{1,2})\s+"
    r"(Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre)"
    r"\s+(\d{2})\s+",
    re.IGNORECASE | re.MULTILINE,
)
# Amount is always the rightmost number (digits/dots/commas) possibly followed by `-`
_AMOUNT_RE = re.compile(r"([\d.]+,\d{2})(-?)\s*$")
# Operation number at start of middle section: 4-6 digits followed by `*`
_OP_RE     = re.compile(r"^(\d{4,})\s*\*\s+")
# Installment info, e.g. C.01/03 → captures current=01, total=03
_INST_RE   = re.compile(r"\s+C\.(\d{2})/(\d{2})\s*")
# Currency marker ($) inside the line
_DOLLAR_RE = re.compile(r"\s+\$\s*")


def _parse_macro_amount(raw: str, negative_suffix: str) -> float:
    """Parse European-format amount: 1.475.973,02 → 1475973.02"""
    value = float(raw.replace(".", "").replace(",", "."))
    return -value if negative_suffix == "-" else value


def _parse_macro_line(line: str) -> Optional[dict]:
    """Parse one text line from a Macro credit card statement.

    Returns a dict with keys date/description/amount, or None if the line
    should be skipped.
    """
    if _SKIP_RE.search(line):
        return None

    date_m = _DATE_RE.match(line)
    if not date_m:
        return None

    amount_m = _AMOUNT_RE.search(line)
    if not amount_m:
        return None

    # Build date (2-digit year → 21st century)
    day   = int(date_m.group(1))
    month = _SPANISH_MONTHS[date_m.group(2).lower()]
    year  = 2000 + int(date_m.group(3))
    try:
        parsed_date = date(year, month, day)
    except ValueError:
        return None

    amount = _parse_macro_amount(amount_m.group(1), amount_m.group(2))

    # Everything between the date and the amount is description + optional codes
    middle = line[date_m.end(): amount_m.start()].strip()

    # Remove operation number (4-6 digits + *)
    op_m = _OP_RE.match(middle)
    if op_m:
        middle = middle[op_m.end():]

    # Extract and remove installment info (C.XX/XX)
    inst_m = _INST_RE.search(middle)
    installment_current = None
    installment_total = None
    if inst_m:
        installment_current = int(inst_m.group(1))
        installment_total = int(inst_m.group(2))
    middle = _INST_RE.sub(" ", middle)

    # Remove currency marker ($)
    middle = _DOLLAR_RE.sub(" ", middle)

    # Collapse internal whitespace
    description = re.sub(r"\s{2,}", " ", middle).strip()

    if not description:
        return None

    return {"date": parsed_date, "description": description, "amount": amount,
            "installment_current": installment_current, "installment_total": installment_total}


def _is_macro_format(text: str) -> bool:
    """Return True if the text looks like a Macro credit card statement."""
    return bool(_DATE_RE.search(text))


# ---------------------------------------------------------------------------
# BBVA credit card text parser  (DD-MonthAbbr-YY  format, Argentina)
# ---------------------------------------------------------------------------

_BBVA_MONTHS = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
}

# Date: 31-Dic-25
_BBVA_DATE_RE = re.compile(
    r"^(\d{1,2})-(Ene|Feb|Mar|Abr|May|Jun|Jul|Ago|Sep|Oct|Nov|Dic)-(\d{2})\b",
    re.IGNORECASE | re.MULTILINE,
)
# End of line: [C.XX/XX ] 6-digit-coupon  peso-amount  [optional-dollar-amount]
_BBVA_END_RE = re.compile(
    r"(?:C\.(\d{2})/(\d{2})\s+)?\b(\d{6})\b\s+([\d.]+,\d{2})(?:\s+[\d.,]+)?\s*$"
)
_BBVA_SKIP_RE = re.compile(r"TOTAL CONSUMOS", re.IGNORECASE)


def _parse_bbva_line(line: str) -> Optional[dict]:
    line = line.strip()
    if _BBVA_SKIP_RE.search(line):
        return None

    date_m = _BBVA_DATE_RE.match(line)
    if not date_m:
        return None

    day   = int(date_m.group(1))
    month = _BBVA_MONTHS[date_m.group(2).lower()]
    year  = 2000 + int(date_m.group(3))
    try:
        parsed_date = date(year, month, day)
    except ValueError:
        return None

    after_date = line[date_m.end():].strip()
    end_m = _BBVA_END_RE.search(after_date)
    if not end_m:
        return None

    installment_current = int(end_m.group(1)) if end_m.group(1) else None
    installment_total   = int(end_m.group(2)) if end_m.group(2) else None
    amount = _parse_macro_amount(end_m.group(4), "")

    description = after_date[: end_m.start()].strip()
    description = re.sub(r"\s{2,}", " ", description).strip()
    if not description:
        return None

    return {
        "date": parsed_date,
        "description": description,
        "amount": amount,
        "installment_current": installment_current,
        "installment_total": installment_total,
    }


def _is_bbva_format(text: str) -> bool:
    return bool(_BBVA_DATE_RE.search(text))


def _parse_bbva_text(text: str, source_name: str, source_type: str = "credit_card_bbva") -> list[dict]:
    transactions = []
    for line in text.splitlines():
        item = _parse_bbva_line(line)
        if item:
            transactions.append({
                **item,
                "source": source_name,
                "source_type": source_type,
            })
    return transactions


def _parse_macro_text(text: str, source_name: str, source_type: str = "pdf") -> list[dict]:
    """Parse all transaction lines from Macro credit card text."""
    transactions = []
    for line in text.splitlines():
        item = _parse_macro_line(line)
        if item:
            transactions.append({
                **item,
                "source": source_name,
                "source_type": source_type,
            })
    return transactions


# ---------------------------------------------------------------------------
# Generic table-based parser (fallback)
# ---------------------------------------------------------------------------

DATE_COLS   = ["fecha", "date", "fecha_operacion", "fecha operacion", "fec", "f.operacion"]
DESC_COLS   = ["descripcion", "descripción", "description", "concepto", "detalle", "movimiento"]
AMOUNT_COLS = ["importe", "amount", "monto", "valor"]
DEBIT_COLS  = ["debito", "débito", "debit", "cargo", "egreso"]
CREDIT_COLS = ["credito", "crédito", "credit", "abono", "ingreso"]


def _find_column(df_columns: list[str], candidates: list[str]) -> Optional[str]:
    lower_map = {c.lower().strip(): c for c in df_columns}
    for candidate in candidates:
        if candidate in lower_map:
            return lower_map[candidate]
    return None


def parse_pdf(file, source_name: str) -> list[dict]:
    try:
        pdf = pdfplumber.open(file)
    except Exception as exc:
        raise ValueError(f"Cannot open PDF file: {exc}")

    # Extract full text from all pages
    full_text = "\n".join(
        page.extract_text() or "" for page in pdf.pages
    )

    # --- Try Macro fixed-width text format first ---
    if _is_macro_format(full_text):
        pdf.close()
        transactions = _parse_macro_text(full_text, source_name)
        if transactions:
            return transactions
        raise ValueError("Macro format detected but no transactions could be parsed. Check the PDF content.")

    # --- Fallback: generic table extraction ---
    all_rows: list[list] = []
    headers: Optional[list[str]] = None

    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if not table:
                continue
            if headers is None:
                headers = [str(h).strip() if h else f"col_{i}" for i, h in enumerate(table[0])]
                all_rows.extend(table[1:])
            else:
                all_rows.extend(table)

    pdf.close()

    if headers is None or not all_rows:
        raise ValueError("No tables found in the PDF. Please verify the file contains tabular data.")

    df = pd.DataFrame(all_rows, columns=headers)

    date_col   = _find_column(list(df.columns), DATE_COLS)
    desc_col   = _find_column(list(df.columns), DESC_COLS)
    amount_col = _find_column(list(df.columns), AMOUNT_COLS)
    debit_col  = _find_column(list(df.columns), DEBIT_COLS)
    credit_col = _find_column(list(df.columns), CREDIT_COLS)

    if not date_col or not desc_col:
        raise ValueError(
            f"Could not auto-detect required columns (date, description) in the PDF. "
            f"Detected columns: {list(df.columns)}. "
            "Please adapt the parser in backend/parsers/pdf_parser.py."
        )

    transactions = []
    for _, row in df.iterrows():
        raw_date = row[date_col]
        try:
            parsed_date = pd.to_datetime(raw_date, dayfirst=True).date()
        except Exception:
            continue

        description = str(row[desc_col]).strip()
        if not description or description.lower() == "nan":
            continue

        if amount_col:
            try:
                amount = float(str(row[amount_col]).replace(",", ".").replace(" ", ""))
            except (ValueError, TypeError):
                amount = 0.0
        elif debit_col and credit_col:
            try:
                debit = float(str(row[debit_col]).replace(",", ".") or 0)
            except (ValueError, TypeError):
                debit = 0.0
            try:
                credit = float(str(row[credit_col]).replace(",", ".") or 0)
            except (ValueError, TypeError):
                credit = 0.0
            amount = credit - debit
        else:
            raise ValueError(
                f"Could not detect amount column. Detected columns: {list(df.columns)}. "
                "Please adapt the parser in backend/parsers/pdf_parser.py."
            )

        transactions.append(
            {
                "date": parsed_date,
                "description": description,
                "amount": amount,
                "source": source_name,
                "source_type": "pdf",
            }
        )

    return transactions
