import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Set DATABASE_URL env var to your Neon PostgreSQL connection string.
# Example: postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'sqlite:///./finances.db'  # fallback for local dev without Neon
)

# SQLite needs check_same_thread=False; PostgreSQL does not need it
_connect_args = {'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def run_migrations():
    """Add new columns to existing tables without Alembic."""
    with engine.begin() as conn:
        if DATABASE_URL.startswith('sqlite'):
            existing = [
                row[1] for row in conn.execute(text("PRAGMA table_info(transactions)")).fetchall()
            ]
            if 'statement_period' not in existing:
                conn.execute(text("ALTER TABLE transactions ADD COLUMN statement_period VARCHAR"))
        else:
            # PostgreSQL
            conn.execute(text("""
                ALTER TABLE transactions
                ADD COLUMN IF NOT EXISTS statement_period VARCHAR
            """))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
