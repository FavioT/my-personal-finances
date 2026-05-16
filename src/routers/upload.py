from collections import Counter
from flask import Blueprint, jsonify, request, g
from models import Transaction
from schemas import TransactionResponse
from parsers import xls_parser, credit_card_parser

bp = Blueprint('upload_api', __name__, url_prefix='/api/upload')


def _detect_period(parsed: list[dict]) -> str | None:
    """Infer the statement period (YYYY-MM) as the most frequent month in the transactions."""
    if not parsed:
        return None
    counts = Counter(t['date'].strftime('%Y-%m') for t in parsed)
    return counts.most_common(1)[0][0]


def _save_transactions(
    db,
    parsed: list[dict],
    source_type: str,
    statement_period: str | None,
    replace_all_for_source_type: bool = False,
) -> list:
    """Replace previous rows then insert new ones.

    - For credit cards, we can replace the full source_type history.
    - For bank XLS, we keep period-based replacement.
    """
    if replace_all_for_source_type:
        db.query(Transaction).filter(
            Transaction.source_type == source_type,
        ).delete(synchronize_session=False)
        db.flush()
    elif statement_period:
        db.query(Transaction).filter(
            Transaction.source_type == source_type,
            Transaction.statement_period == statement_period,
        ).delete(synchronize_session=False)
        db.flush()

    db_transactions = []
    for item in parsed:
        item['statement_period'] = statement_period
        tx = Transaction(**item)
        db.add(tx)
        db_transactions.append(tx)
    db.commit()
    for tx in db_transactions:
        db.refresh(tx)
    return db_transactions


@bp.post('/xls')
def upload_xls():
    db = g.db
    if 'file' not in request.files:
        return jsonify({'detail': 'No file provided'}), 400
    file = request.files['file']
    try:
        parsed = xls_parser.parse_xls(file, source_name=file.filename)
    except Exception as e:
        return jsonify({'detail': str(e)}), 400
    period = _detect_period(parsed)
    txs = _save_transactions(db, parsed, source_type='xls', statement_period=period)
    return jsonify({
        'transactions': [TransactionResponse.model_validate(t).model_dump(mode='json') for t in txs],
        'statement_period': period,
        'replaced': True,
    })


def _upload_credit_card(bank: str, source_type: str, replace_all_for_source_type: bool = False):
    db   = g.db
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'detail': 'Missing text field'}), 400
    # Allow manual period override from the UI
    manual_period = data.get('statement_period') or None
    try:
        parsed = credit_card_parser.parse_credit_card_text(data['text'], bank=bank)
    except Exception as e:
        return jsonify({'detail': str(e)}), 400
    period = manual_period or _detect_period(parsed)
    txs = _save_transactions(
        db,
        parsed,
        source_type=source_type,
        statement_period=period,
        replace_all_for_source_type=replace_all_for_source_type,
    )
    return jsonify({
        'transactions': [TransactionResponse.model_validate(t).model_dump(mode='json') for t in txs],
        'statement_period': period,
        'replaced': True,
    })


@bp.post('/credit-card/bbva')
def upload_credit_card_bbva():
    return _upload_credit_card('bbva', 'credit_card_bbva')


@bp.post('/credit-card/bbva-visa')
def upload_credit_card_bbva_visa():
    return _upload_credit_card('bbva_visa', 'credit_card_bbva_visa', replace_all_for_source_type=True)


@bp.post('/credit-card/bbva-mastercard')
def upload_credit_card_bbva_mastercard():
    return _upload_credit_card('bbva_mastercard', 'credit_card_bbva_mastercard', replace_all_for_source_type=True)


@bp.post('/credit-card/macro')
def upload_credit_card_macro():
    return _upload_credit_card('macro', 'credit_card_macro', replace_all_for_source_type=True)


@bp.delete('/credit-card/period')
def delete_period():
    """Delete all transactions for a given source_type + statement_period."""
    db   = g.db
    data = request.get_json()
    if not data or 'source_type' not in data or 'statement_period' not in data:
        return jsonify({'detail': 'Missing source_type or statement_period'}), 400
    deleted = db.query(Transaction).filter(
        Transaction.source_type == data['source_type'],
        Transaction.statement_period == data['statement_period'],
    ).delete(synchronize_session=False)
    db.commit()
    return jsonify({'deleted': deleted})
