import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app
from app.database import get_db
from app.models.employee import Employee
from app.models.enums import EmployeeStatus
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    db = MagicMock()
    return db

def test_create_employee_returns_201(monkeypatch):
    mock_db = MagicMock()
    # Mock no existing employee
    mock_db.query().filter().first.return_value = None

    def mock_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = mock_get_db

    # Setup refresh behavior to populate id and created_at
    def mock_refresh(emp):
        emp.id = 1
        emp.created_at = datetime.utcnow()

    mock_db.refresh.side_effect = mock_refresh

    payload = {
        "fullName": "Alice Smith",
        "email": "alice@example.com",
        "department": "Engineering"
    }

    response = client.post("/employees", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["fullName"] == "Alice Smith"
    assert data["email"] == "alice@example.com"

def test_get_employee_by_id_not_found_returns_404():
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None

    def mock_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = mock_get_db

    response = client.get("/employees/999")
    app.dependency_overrides.clear()

    assert response.status_code == 404
    data = response.json()
    assert data["status"] == 404
    assert "not found" in data["message"].lower()
