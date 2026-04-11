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
    installment_current: Optional[int] = None
    installment_total: Optional[int] = None


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


class CreditCardInstallmentItem(BaseModel):
    transaction_id: int
    description: str
    date: date
    monthly_amount: float
    installment_current: int
    installment_total: int
    pending_installments: int
    remaining_debt: float
    total_debt: float
    payoff_month: str  # "YYYY-MM"


class CardSummary(BaseModel):
    card: str
    card_network: str
    total_monthly: float
    total_remaining_debt: float
    total_debt: float
    payoff_month: str
    items: list[CreditCardInstallmentItem]


class CreditCardSummaryResponse(BaseModel):
    cards: list[CardSummary]
