from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from database import engine, Base
from routers import upload, transactions

Base.metadata.create_all(bind=engine)

# Incremental migration: add installment columns if they don't exist yet
for _col in ["installment_current INTEGER", "installment_total INTEGER"]:
    try:
        with engine.connect() as _conn:
            _conn.execute(text(f"ALTER TABLE transactions ADD COLUMN {_col}"))
            _conn.commit()
    except Exception:
        pass  # column already exists

app = FastAPI(title="My Personal Finances API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])


@app.get("/")
def root():
    return {"message": "My Personal Finances API is running"}
