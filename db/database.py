from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, TGAccount

DATABASE_URL = "sqlite:///tg_accounts.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create the database tables."""
    Base.metadata.create_all(bind=engine)

def get_account_credentials():
    """Retrieve all account credentials from the database."""
    db = SessionLocal()
    try:
        accounts = db.query(TGAccount).all()
        return [(account.api_id, account.api_hash, account.phone_number) for account in accounts]
    finally:
        db.close()
