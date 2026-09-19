"""
One-time CLI script to create an admin account.
Usage: python -m app.create_admin
"""
import getpass
import sys

from app.auth_utils import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Admin


def main():
    Base.metadata.create_all(bind=engine)

    print("=== Create a new admin account ===")
    username = input("Username: ").strip()
    if len(username) < 3:
        print("Username must be at least 3 characters.")
        sys.exit(1)

    password = getpass.getpass("Password (min 8 characters): ")
    if len(password) < 8:
        print("Password must be at least 8 characters.")
        sys.exit(1)

    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match.")
        sys.exit(1)

    db = SessionLocal()
    try:
        existing = db.query(Admin).filter(Admin.username == username).first()
        if existing:
            print(f"An admin with username '{username}' already exists.")
            sys.exit(1)

        admin = Admin(username=username, password_hash=hash_password(password))
        db.add(admin)
        db.commit()
        print(f"Admin '{username}' created successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
