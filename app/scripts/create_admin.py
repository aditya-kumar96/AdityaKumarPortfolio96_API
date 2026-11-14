from getpass import getpass 
from sqlalchemy import Select
from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.models.admin import Admin
from app.core.security import hash_password


def create_admin():
    db = SessionLocal()
    
    try:
        email = input("Enter admin email: ").strip().lower()
        if not email:
            print("Email cannot be empty")
            return
        
        existing_admin = db.scalar(Select(Admin).where(Admin.email == email))
        
        if existing_admin :
            print("An admin with email already exists")
            return
        
        password = getpass("Enter password")
        confirm_pass = getpass("Confirm Password")
        
        if len(password) < 4:
            print("password should be 4 digit long")
            return
        hashed_password = hash_password(password)
        admin = Admin(
            email = email,
            hashed_password = hashed_password,
            is_active = True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print(f"Admin account created ")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
        
if __name__ == "__main__":
    create_admin()

        
#adityk@gmail.com
#chetu123