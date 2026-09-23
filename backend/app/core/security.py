from passlib.context import CryptContext
from datetime import datetime, timedelta
import secrets

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def generate_session_identifier() -> str:
    return secrets.token_urlsafe(32)

def generate_temporary_password() -> str:
    return secrets.token_urlsafe(12)
