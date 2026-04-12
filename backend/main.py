import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env before any other local imports so DATABASE_URL is available
# when database.py creates the SQLAlchemy engine.
# Looks for .env in the backend/ dir first, then the project root.
load_dotenv(dotenv_path=Path(__file__).parent / '.env')
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import upload, transactions

# Creates all tables if they don't exist (works with both SQLite and PostgreSQL)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="My Personal Finances API", version="1.0.0")

# CORS: allow localhost for dev + any Vercel deployment URL via env var
_extra_origin = os.environ.get('FRONTEND_ORIGIN', '')
_origins = [
    'http://localhost:4200',
    'http://localhost:4201',
]
if _extra_origin:
    _origins.append(_extra_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(upload.router, prefix='/upload', tags=['upload'])
app.include_router(transactions.router, prefix='/transactions', tags=['transactions'])


@app.get('/')
def root():
    return {'message': 'My Personal Finances API is running'}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
