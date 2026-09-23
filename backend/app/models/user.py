import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from app.db.database import Base

# Utility for dialect-agnostic UUID handling if needed, but we can just use String for SQLite compatibility during tests
# For simplicity in testing with SQLite, we'll use String(36) to store UUIDs if not strictly pg
import os
from app.core.config import settings

def UUID_COL():
    return String(36)

class User(Base):
    __tablename__ = "users"

    id = Column(UUID_COL(), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, default="CANDIDATE")
    status = Column(String, default="ACTIVE")
    must_change_password = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    credential = relationship("UserCredential", back_populates="user", uselist=False)
    profile = relationship("Profile", back_populates="user", uselist=False)
    sessions = relationship("Session", back_populates="user")


class UserCredential(Base):
    __tablename__ = "user_credentials"

    id = Column(UUID_COL(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID_COL(), ForeignKey("users.id"), unique=True)
    password_hash = Column(String, nullable=False)
    password_changed_at = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="credential")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID_COL(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID_COL(), ForeignKey("users.id"), unique=True)
    full_name = Column(String, nullable=False)
    target_force = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID_COL(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID_COL(), ForeignKey("users.id"))
    session_identifier = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="sessions")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID_COL(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID_COL(), ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_info = Column(JSON, nullable=True) # avoiding `metadata` as it is a reserved SQLAlchemy Base keyword
