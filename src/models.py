from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="ARS")
    category = Column(String, nullable=True)
    source = Column(String, nullable=False)
    source_type = Column(String, nullable=False)  # "xls", "pdf", "credit_card_bbva", "credit_card_macro"
    installment_current = Column(Integer, nullable=True)
    installment_total = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
