import uuid
from sqlalchemy.orm import Session

from app.models.user_model import User, UserRole, PasswordResetOTP
from app.schemas.user_schema import UserCreate, UserUpdate, AdminCreateUser
from app.core.security import hash_password, verify_password
from app.core.config import settings



def create_user(db: Session, data: UserCreate):
    existing_user = db.query(User).filter(User.email == data.email).first()

    if existing_user:
        return None

    user = User(
        full_name=data.full_name,
        email=data.email,
        password=hash_password(data.password),
        role=UserRole.USER,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def admin_create_user(db: Session, data: AdminCreateUser):
    existing_user = db.query(User).filter(User.email == data.email).first()

    if existing_user:
        return None

    user = User(
        full_name=data.full_name,
        email=data.email,
        password=hash_password(data.password),
        role=data.role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    if not user.is_active:
        return None

    return user


def get_user_by_id(db: Session, user_id: uuid.UUID):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session):
    return db.query(User).order_by(User.created_at.desc()).all()



def update_user(db: Session, user_id: uuid.UUID, data: UserUpdate):
    user = get_user_by_id(db, user_id)

    if not user:
        return None

    if data.full_name is not None:
        user.full_name = data.full_name

    if data.email is not None:
        user.email = data.email

    if data.profile_photo_url is not None:
        user.profile_photo_url = data.profile_photo_url

    if data.bio is not None:
        user.bio = data.bio

    if data.date_of_birth is not None:
        user.date_of_birth = data.date_of_birth

    if data.gender is not None:
        user.gender = data.gender

    if data.nationality is not None:
        user.nationality = data.nationality

    if data.phone_number is not None:
        user.phone_number = data.phone_number

    if data.address is not None:
        user.address = data.address

    db.commit()
    db.refresh(user)

    return user


def update_user_role(db: Session, user_id: uuid.UUID, role: UserRole):
    user = get_user_by_id(db, user_id)

    if not user:
        return None

    user.role = role

    db.commit()
    db.refresh(user)

    return user


def delete_user(db: Session, user_id: uuid.UUID):
    user = get_user_by_id(db, user_id)

    if not user:
        return None

    db.delete(user)
    db.commit()

    return user