import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# On Vercel (read-only filesystem) the DB lives in /tmp.
# Locally it lives next to the backend folder.
_DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), 'finances.db')
_db_path = os.environ.get('DATABASE_PATH', _DEFAULT_DB_PATH)
DATABASE_URL = f'sqlite:///{_db_path}'

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
