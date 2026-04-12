import os
import hmac
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / '.env')
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

from flask import Flask, g, redirect, url_for, render_template, request, session, jsonify
from database import engine, Base, SessionLocal

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"[warn] create_all failed: {e}")

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
app.secret_key = os.environ.get('SECRET_KEY', 'dev-insecure-key')

_APP_PIN = os.environ.get('APP_PIN', '')
_PUBLIC_ENDPOINTS = {'login', 'login_post', 'static'}
_MAX_ATTEMPTS = 5
_LOCKOUT_SECONDS = 300  # 5 minutos


@app.before_request
def require_pin():
    if request.endpoint in _PUBLIC_ENDPOINTS:
        return
    if session.get('authenticated'):
        return
    return redirect(url_for('login'))


@app.before_request
def open_db():
    g.db = SessionLocal()


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db:
        db.close()


@app.get('/login')
def login():
    return render_template('login.html', error=None)


@app.post('/login')
def login_post():
    # Lockout check
    locked_until = session.get('locked_until', 0)
    if time.time() < locked_until:
        remaining = int(locked_until - time.time())
        return render_template('login.html', error=f'Demasiados intentos. Esperá {remaining} segundos.')

    pin = request.form.get('pin', '')
    if _APP_PIN and hmac.compare_digest(pin, _APP_PIN):
        session['authenticated'] = True
        session.pop('attempts', None)
        session.pop('locked_until', None)
        return redirect(url_for('dashboard'))

    attempts = session.get('attempts', 0) + 1
    session['attempts'] = attempts
    if attempts >= _MAX_ATTEMPTS:
        session['locked_until'] = time.time() + _LOCKOUT_SECONDS
        session['attempts'] = 0
        return render_template('login.html', error=f'Demasiados intentos. Esperá {_LOCKOUT_SECONDS // 60} minutos.')
    return render_template('login.html', error=f'PIN incorrecto. ({attempts}/{_MAX_ATTEMPTS} intentos)')


@app.get('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

from routers.transactions import bp as transactions_bp  # noqa: E402
from routers.upload import bp as upload_bp              # noqa: E402

app.register_blueprint(transactions_bp)
app.register_blueprint(upload_bp)


@app.get('/')
def index():
    return redirect(url_for('dashboard'))


@app.get('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.get('/transactions')
def transactions_page():
    return render_template('transactions.html')


@app.get('/upload')
def upload_page():
    return render_template('upload.html')


@app.get('/credit-cards')
def credit_cards_page():
    return render_template('credit_cards.html')


if __name__ == '__main__':
    app.run(debug=True, port=8000)
