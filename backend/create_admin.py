import getpass

from app.database import SessionLocal
from app.models import User
from app.security import hash_password


def main():
    db = SessionLocal()
    try:
        full_name = input("Full name: ").strip()
        email = input("Email: ").strip().lower()
        password = getpass.getpass("Password (8-72 chars): ")

        if not full_name or not email:
            print("Name and email are required.")
            return
        if not 8 <= len(password.encode("utf-8")) <= 72:
            print("Password must be 8 to 72 characters.")
            return
        if db.query(User).filter(User.email == email).first():
            print("A user with this email already exists.")
            return

        db.add(User(
            full_name=full_name,
            email=email,
            hashed_password=hash_password(password),
            role="admin",
            is_active=True,
        ))
        db.commit()
        print(f"Admin created: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()