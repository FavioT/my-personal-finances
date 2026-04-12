from datetime import date
from flask import Blueprint, jsonify, request, g
from models import Transaction
from schemas import (
    TransactionResponse, SummaryResponse,
    CreditCardSummaryResponse, CardSummary, CreditCardInstallmentItem,
)

bp = Blueprint('transactions_api', __name__, url_prefix='/api/transactions')


@bp.get('')
def get_transactions():
    db = g.db
    source_type = request.args.get('source_type')
    date_from   = request.args.get('date_from')
    date_to     = request.args.get('date_to')

    query = db.query(Transaction)
    if source_type:
        query = query.filter(Transaction.source_type == source_type)
    else:
        query = query.filter(~Transaction.source_type.like('credit_card_%'))
    if date_from:
        query = query.filter(Transaction.date >= date.fromisoformat(date_from))
    if date_to:
        query = query.filter(Transaction.date <= date.fromisoformat(date_to))

    txs = query.order_by(Transaction.date.desc()).all()
    return jsonify([TransactionResponse.model_validate(t).model_dump(mode='json') for t in txs])


@bp.get('/summary')
def get_summary():
    db = g.db
    txs = db.query(Transaction).all()
    total_income   = sum(t.amount for t in txs if t.amount > 0)
    total_expenses = sum(t.amount for t in txs if t.amount < 0)
    balance        = total_income + total_expenses
    return jsonify(SummaryResponse(
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        balance=round(balance, 2),
    ).model_dump())


@bp.delete('/<int:transaction_id>')
def delete_transaction(transaction_id):
    db = g.db
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        return jsonify({'detail': 'Transaction not found'}), 404
    db.delete(tx)
    db.commit()
    return '', 204


_CARD_NETWORKS = {
    'BBVA': 'VISA',
    'BBVA_VISA': 'VISA',
    'BBVA_MASTERCARD': 'Mastercard',
    'MACRO': 'Mastercard',
}


def _add_months(d: date, months: int) -> date:
    total = d.month + months
    year  = d.year + (total - 1) // 12
    month = (total - 1) % 12 + 1
    return date(year, month, 1)


@bp.get('/credit-card-summary')
def get_credit_card_summary():
    db = g.db
    txs = (
        db.query(Transaction)
        .filter(Transaction.source_type.in_([
            'credit_card_bbva',
            'credit_card_bbva_visa',
            'credit_card_bbva_mastercard',
            'credit_card_macro',
        ]))
        .order_by(Transaction.date)
        .all()
    )

    by_card: dict[str, list] = {}
    for tx in txs:
        by_card.setdefault(tx.source, []).append(tx)

    cards = []
    for card, card_txs in by_card.items():
        items = []
        for tx in card_txs:
            inst_current = tx.installment_current if tx.installment_current is not None else 1
            inst_total   = tx.installment_total   if tx.installment_total   is not None else 1
            pending      = inst_total - inst_current
            payoff       = _add_months(tx.date, pending)
            monthly      = abs(tx.amount)
            items.append(CreditCardInstallmentItem(
                transaction_id=tx.id,
                description=tx.description,
                date=tx.date,
                monthly_amount=round(monthly, 2),
                installment_current=inst_current,
                installment_total=inst_total,
                pending_installments=pending,
                remaining_debt=round(monthly * pending, 2),
                total_debt=round(monthly * inst_total, 2),
                payoff_month=payoff.strftime('%Y-%m'),
            ))

        payoff_month = max(i.payoff_month for i in items) if items else ''
        cards.append(CardSummary(
            card=card,
            card_network=_CARD_NETWORKS.get(card, card),
            total_monthly=round(sum(i.monthly_amount for i in items), 2),
            total_remaining_debt=round(sum(i.remaining_debt for i in items), 2),
            total_debt=round(sum(i.total_debt for i in items), 2),
            payoff_month=payoff_month,
            items=items,
        ))

    return jsonify(CreditCardSummaryResponse(cards=cards).model_dump(mode='json'))
