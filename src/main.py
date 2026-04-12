import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / '.env')
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

from flask import Flask, g, redirect, url_for, render_template
from database import engine, Base, SessionLocal

Base.metadata.create_all(bind=engine)

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))


@app.before_request
def open_db():
    g.db = SessionLocal()


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db:
        db.close()


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
