from typing import List
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models import Transaction
from schemas import TransactionResponse, CreditCardTextInput
from parsers import xls_parser, credit_card_parser

router = APIRouter()


def _save_transactions(db: Session, parsed: list[dict]) -> List[Transaction]:
    db_transactions = []
    for item in parsed:
        tx = Transaction(**item)
        db.add(tx)
        db_transactions.append(tx)
    db.commit()
    for tx in db_transactions:
        db.refresh(tx)
    return db_transactions


@router.post("/xls", response_model=List[TransactionResponse])
async def upload_xls(file: UploadFile = File(...), db: Session = Depends(get_db)):
    parsed = xls_parser.parse_xls(file.file, source_name=file.filename)
    return _save_transactions(db, parsed)


@router.post("/credit-card/bbva", response_model=List[TransactionResponse])
async def upload_credit_card_bbva(body: CreditCardTextInput, db: Session = Depends(get_db)):
    parsed = credit_card_parser.parse_credit_card_text(body.text, bank="bbva")
    return _save_transactions(db, parsed)


@router.post("/credit-card/macro", response_model=List[TransactionResponse])
async def upload_credit_card_macro(body: CreditCardTextInput, db: Session = Depends(get_db)):
    parsed = credit_card_parser.parse_credit_card_text(body.text, bank="macro")
    return _save_transactions(db, parsed)
