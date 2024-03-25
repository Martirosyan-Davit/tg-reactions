from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TGAccount(Base):
    """
    Represents a Telegram account in the database.

    Attributes:
        id (int): The unique identifier for the account.
        api_id (str): The API ID associated with the account.
        api_hash (str): The API hash associated with the account.
        phone_number (str): The phone number associated with the account.
        proxy_credentials (dict): The proxy credentials associated with the account in JSON format.
    """
    __tablename__ = 'tg_accounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    api_id = Column(String, nullable=False, unique=True)
    api_hash = Column(String, nullable=False)
    phone_number = Column(String, nullable=False, unique=True)
    proxy_credentials = Column(JSON, nullable=False)
