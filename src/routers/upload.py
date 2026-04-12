from flask import Blueprint, jsonify, request, g
from models import Transaction
from schemas import TransactionResponse
from parsers import xls_parser, credit_card_parser

bp = Blueprint('upload_api', __name__, url_prefix='/api/upload')


def _save_transactions(db, parsed: list[dict]) -> list:
    db_transactions = []
    for item in parsed:
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
    txs = _save_transactions(db, parsed)
    return jsonify([TransactionResponse.model_validate(t).model_dump(mode='json') for t in txs])


@bp.post('/credit-card/bbva')
def upload_credit_card_bbva():
    db   = g.db
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'detail': 'Missing text field'}), 400
    try:
        parsed = credit_card_parser.parse_credit_card_text(data['text'], bank='bbva')
    except Exception as e:
        return jsonify({'detail': str(e)}), 400
    txs = _save_transactions(db, parsed)
    return jsonify([TransactionResponse.model_validate(t).model_dump(mode='json') for t in txs])


@bp.post('/credit-card/bbva-visa')
def upload_credit_card_bbva_visa():
    db   = g.db
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'detail': 'Missing text field'}), 400
    try:
        parsed = credit_card_parser.parse_credit_card_text(data['text'], bank='bbva_visa')
    except Exception as e:
        return jsonify({'detail': str(e)}), 400
    txs = _save_transactions(db, parsed)
    return jsonify([TransactionResponse.model_validate(t).model_dump(mode='json') for t in txs])


@bp.post('/credit-card/bbva-mastercard')
def upload_credit_card_bbva_mastercard():
    db   = g.db
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'detail': 'Missing text field'}), 400
    try:
        parsed = credit_card_parser.parse_credit_card_text(data['text'], bank='bbva_mastercard')
    except Exception as e:
        return jsonify({'detail': str(e)}), 400
    txs = _save_transactions(db, parsed)
    return jsonify([TransactionResponse.model_validate(t).model_dump(mode='json') for t in txs])


@bp.post('/credit-card/macro')
def upload_credit_card_macro():
    db   = g.db
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'detail': 'Missing text field'}), 400
    try:
        parsed = credit_card_parser.parse_credit_card_text(data['text'], bank='macro')
    except Exception as e:
        return jsonify({'detail': str(e)}), 400
    txs = _save_transactions(db, parsed)
    return jsonify([TransactionResponse.model_validate(t).model_dump(mode='json') for t in txs])
