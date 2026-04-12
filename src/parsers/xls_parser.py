from typing import Optional
import io
import pandas as pd
from fastapi import HTTPException


# Common column name mappings (lowercase)
DATE_COLS = ["fecha", "date", "fecha_operacion", "fecha operacion", "fec", "f.operacion"]
DESC_COLS = ["descripcion", "descripción", "description", "concepto", "detalle", "movimiento"]
AMOUNT_COLS = ["importe", "amount", "monto", "valor"]
DEBIT_COLS = ["debito", "débito", "debit", "cargo", "egreso"]
CREDIT_COLS = ["credito", "crédito", "credit", "abono", "ingreso"]


def _find_column(df_columns: list[str], candidates: list[str]) -> Optional[str]:
    lower_map = {c.lower().strip(): c for c in df_columns}
    for candidate in candidates:
        if candidate in lower_map:
            return lower_map[candidate]
    return None


def _detect_header_row(content: bytes) -> int:
    """Scan the first 15 rows to find the one that contains date/description headers."""
    try:
        preview = pd.read_excel(io.BytesIO(content), header=None, nrows=15)
        for i, row in preview.iterrows():
            values_lower = [str(v).lower().strip() for v in row.values]
            has_date = any(v in DATE_COLS for v in values_lower)
            has_desc = any(v in DESC_COLS for v in values_lower)
            if has_date and has_desc:
                return int(i)
    except Exception:
        pass
    return 0


def _parse_amount(raw) -> float:
    """Parse European-format numbers (1.234.567,89 → 1234567.89)."""
    s = str(raw).strip().replace("\xa0", "").replace(" ", "")
    if not s or s.lower() == "nan":
        return 0.0
    # Dots are thousands separators, comma is decimal separator
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def parse_xls(file, source_name: str) -> list[dict]:
    content = file.read()

    header_row = _detect_header_row(content)

    try:
        df = pd.read_excel(io.BytesIO(content), header=header_row)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Cannot read Excel file: {exc}")

    if df.empty:
        raise HTTPException(status_code=400, detail="The Excel file is empty.")

    columns = list(df.columns)

    date_col = _find_column(columns, DATE_COLS)
    desc_col = _find_column(columns, DESC_COLS)
    amount_col = _find_column(columns, AMOUNT_COLS)
    debit_col = _find_column(columns, DEBIT_COLS)
    credit_col = _find_column(columns, CREDIT_COLS)

    if not date_col or not desc_col:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Could not auto-detect required columns (date, description) in the file. "
                f"Detected columns: {columns}. "
                "Please adapt the parser in backend/parsers/xls_parser.py."
            ),
        )

    # If a nameless column sits immediately after the description column,
    # treat it as additional description context (e.g. bank channel / branch).
    desc_col_idx = columns.index(desc_col)
    extra_desc_col: Optional[str] = None
    if desc_col_idx + 1 < len(columns) and str(columns[desc_col_idx + 1]).startswith("Unnamed:"):
        extra_desc_col = columns[desc_col_idx + 1]

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

        if extra_desc_col:
            extra = str(row[extra_desc_col]).strip()
            if extra and extra.lower() != "nan":
                description = f"{description} | {extra}"

        if amount_col:
            amount = _parse_amount(row[amount_col])
        elif debit_col and credit_col:
            amount = _parse_amount(row[credit_col]) - _parse_amount(row[debit_col])
        else:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Could not detect amount column. Detected columns: {columns}. "
                    "Please adapt the parser in backend/parsers/xls_parser.py."
                ),
            )

        transactions.append(
            {
                "date": parsed_date,
                "description": description,
                "amount": amount,
                "source": source_name,
                "source_type": "xls",
            }
        )

    return transactions
