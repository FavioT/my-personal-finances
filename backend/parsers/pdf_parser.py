from typing import Optional
import pdfplumber
import pandas as pd
from fastapi import HTTPException


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


def parse_pdf(file, source_name: str) -> list[dict]:
    try:
        pdf = pdfplumber.open(file)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Cannot open PDF file: {exc}")

    all_rows: list[list] = []
    headers: Optional[list[str]] = None

    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if not table:
                continue
            if headers is None and table:
                headers = [str(h).strip() if h else f"col_{i}" for i, h in enumerate(table[0])]
                all_rows.extend(table[1:])
            else:
                all_rows.extend(table)

    pdf.close()

    if headers is None or not all_rows:
        raise HTTPException(
            status_code=400,
            detail="No tables found in the PDF. Please verify the file contains tabular data.",
        )

    df = pd.DataFrame(all_rows, columns=headers)

    date_col = _find_column(list(df.columns), DATE_COLS)
    desc_col = _find_column(list(df.columns), DESC_COLS)
    amount_col = _find_column(list(df.columns), AMOUNT_COLS)
    debit_col = _find_column(list(df.columns), DEBIT_COLS)
    credit_col = _find_column(list(df.columns), CREDIT_COLS)

    if not date_col or not desc_col:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Could not auto-detect required columns (date, description) in the PDF. "
                f"Detected columns: {list(df.columns)}. "
                "Please adapt the parser in backend/parsers/pdf_parser.py."
            ),
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
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Could not detect amount column. Detected columns: {list(df.columns)}. "
                    "Please adapt the parser in backend/parsers/pdf_parser.py."
                ),
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
