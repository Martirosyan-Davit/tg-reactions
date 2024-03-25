import argparse
from db.database import SessionLocal, TGAccount

def delete_account(phone_number: str):
    """
    Delete a Telegram account from the database.

    Args:
        phone_number (str): The phone number of the account to delete.

    Returns:
        None
    """
    db = SessionLocal()
    account = db.query(TGAccount).filter_by(phone_number=phone_number).first()

    if account:
        db.delete(account)
        db.commit()
        print(f"Deleted account with phone number {phone_number}.")
    else:
        print(f"No account found with phone number {phone_number}.")

    db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete a Telegram account from the database.")
    parser.add_argument("phone_number", type=str, help="The phone number of the account to delete.")

    args = parser.parse_args()

    delete_account(args.phone_number)
