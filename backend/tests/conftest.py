import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base, get_db
from app.main import app
from app.models.user import User, UserCredential
from app.core.security import get_password_hash

# Use an in-memory SQLite DB for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_pytest.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    import os
    if os.path.exists("./test_pytest.db"):
        try:
            os.remove("./test_pytest.db")
        except PermissionError:
            pass # ignore on Windows if handles still open

@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]

@pytest.fixture
def admin_token_headers(client, db):
    # Create an admin user directly
    user = db.query(User).filter(User.username == "admin_user").first()
    if not user:
        user = User(username="admin_user", role="ADMIN", must_change_password=False)
        db.add(user)
        db.flush()
        cred = UserCredential(user_id=user.id, password_hash=get_password_hash("adminpass"))
        db.add(cred)
        db.commit()

    # Login to get cookie
    response = client.post("/api/v1/auth/login", json={"username": "admin_user", "password": "adminpass"})
    cookie = response.cookies.get("defendx_session")
    return {"Cookie": f"defendx_session={cookie}"}
