from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Transaction
from schemas import TransactionResponse, SummaryResponse

router = APIRouter()


@router.get("", response_model=List[TransactionResponse])
def get_transactions(
    source_type: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Transaction)
    if source_type:
        query = query.filter(Transaction.source_type == source_type)
    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)
    return query.order_by(Transaction.date.desc()).all()


@router.get("/summary", response_model=SummaryResponse)
def get_summary(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).all()
    total_income = sum(t.amount for t in transactions if t.amount > 0)
    total_expenses = sum(t.amount for t in transactions if t.amount < 0)
    balance = total_income + total_expenses
    return SummaryResponse(
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        balance=round(balance, 2),
    )


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(tx)
    db.commit()
