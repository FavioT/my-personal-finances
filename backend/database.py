import os
from sqlalchemy import create_engine
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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
