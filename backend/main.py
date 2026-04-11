import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import upload, transactions
from dotenv import load_dotenv;

load_dotenv()

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
