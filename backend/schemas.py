from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class TransactionBase(BaseModel):
    date: date
    description: str
    amount: float
    currency: str = "ARS"
    category: Optional[str] = None
    source: str
    source_type: str


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SummaryResponse(BaseModel):
    total_income: float
    total_expenses: float
    balance: float


class CreditCardTextInput(BaseModel):
    text: str
