import pytest
from unittest.mock import MagicMock
import httpx
from app.models.employee import Employee
from app.models.enums import EmployeeStatus
from app.adapters.identity_adapter import IdentityRestAdapter
from app.adapters.exceptions import VendorIntegrationException

@pytest.fixture
def sample_employee():
    return Employee(
        id=1,
        full_name="Alice Smith",
        email="alice@example.com",
        department="Engineering",
        status=EmployeeStatus.ACTIVE
    )

def test_create_identity_account_success(sample_employee):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.is_success = True
    mock_response.json.return_value = {
        "accountId": "IDN-1",
        "message": "User created",
        "status": "CREATED"
    }
    mock_client.post.return_value = mock_response

    adapter = IdentityRestAdapter(base_url="http://localhost:8082", client=mock_client)
    res = adapter.create_identity_account(sample_employee)

    assert res.success is True
    assert res.transaction_id == "IDN-1"
    assert res.message == "User created"

def test_create_identity_account_failure_raises_exception(sample_employee):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.is_success = False
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_client.post.return_value = mock_response

    adapter = IdentityRestAdapter(base_url="http://localhost:8082", client=mock_client)

    with pytest.raises(VendorIntegrationException) as exc_info:
        adapter.create_identity_account(sample_employee)

    assert "500" in str(exc_info.value)
