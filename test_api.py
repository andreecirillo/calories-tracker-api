import pytest
from fastapi.testclient import TestClient
from main import app
from models import Base, engine, get_db
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime, timedelta

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_calories.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create test database and tables
Base.metadata.create_all(bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the dependency
app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)

def test_create_entry():
    """Test creating a new food entry"""
    entry_data = {
        "user_id": 1,
        "username": "test_user",
        "food_name": "Test Food",
        "calories": 500,
        "date_time": "2025-05-20T12:00:00"
    }
    
    response = client.post("/api/entries/", json=entry_data)
    assert response.status_code == 201
    data = response.json()
    assert data["food_name"] == "Test Food"
    assert data["calories"] == 500
    assert data["username"] == "test_user"

def test_list_entries():
    """Test listing food entries"""
    # First create a test entry
    entry_data = {
        "user_id": 1,
        "username": "test_user",
        "food_name": "List Test Food",
        "calories": 300,
        "date_time": "2025-05-20T13:00:00"
    }
    client.post("/api/entries/", json=entry_data)
    
    # Now test listing entries
    response = client.get("/api/entries/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(entry["food_name"] == "List Test Food" for entry in data)

def test_get_single_entry():
    """Test retrieving a single food entry"""
    # First create a test entry
    entry_data = {
        "user_id": 1,
        "username": "test_user",
        "food_name": "Single Test Food",
        "calories": 200,
        "date_time": "2025-05-20T14:00:00"
    }
    response = client.post("/api/entries/", json=entry_data)
    entry_id = response.json()["id"]
    
    # Now test getting that specific entry
    response = client.get(f"/api/entries/{entry_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == entry_id
    assert data["food_name"] == "Single Test Food"

# Clean up after tests
@pytest.fixture(autouse=True)
def cleanup():
    # This will run before each test
    Base.metadata.create_all(bind=test_engine)
    yield
    # This will run after each test
    Base.metadata.drop_all(bind=test_engine)
