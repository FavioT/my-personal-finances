from datetime import date
from typing import Optional
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


def parse_xls(file, source_name: str) -> list[dict]:
    try:
        df = pd.read_excel(file)
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

    transactions = []
    for _, row in df.iterrows():
        raw_date = row[date_col]
        try:
            parsed_date = pd.to_datetime(raw_date).date()
        except Exception:
            continue

        description = str(row[desc_col]).strip()
        if not description or description.lower() == "nan":
            continue

        if amount_col:
            try:
                amount = float(str(row[amount_col]).replace(",", "."))
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
