import httpx
import logging
from app.config import settings
from app.schemas.workflow import VendorResponse
from app.adapters.exceptions import VendorIntegrationException

logger = logging.getLogger("IdentityRestAdapter")

class IdentityRestAdapter:
    def __init__(self, base_url: str = None, client: httpx.Client = None):
        self.base_url = base_url or settings.identity_service_url
        self.client = client or httpx.Client(timeout=10.0)

    def create_identity_account(self, employee) -> VendorResponse:
        url = f"{self.base_url}/api/accounts"
        payload = {
            "employeeId": employee.id,
            "fullName": employee.full_name,
            "email": employee.email,
            "department": employee.department
        }
        logger.info(f"Calling Identity REST service at {url} for employee #{employee.id}")
        try:
            res = self.client.post(url, json=payload)
            if res.is_success:
                data = res.json()
                return VendorResponse(
                    success=True,
                    transaction_id=data.get("accountId"),
                    message=data.get("message"),
                    raw_data=data
                )
            else:
                raise VendorIntegrationException(f"Identity service returned status {res.status_code}: {res.text}")
        except VendorIntegrationException:
            raise
        except Exception as ex:
            logger.error(f"Identity service communication failure: {ex}")
            raise VendorIntegrationException(f"Identity service communication failure: {str(ex)}") from ex

    def deactivate_identity_account(self, employee) -> VendorResponse:
        url = f"{self.base_url}/api/accounts/{employee.id}"
        logger.info(f"Calling Identity REST service at {url} to deactivate employee #{employee.id}")
        try:
            res = self.client.delete(url)
            if res.is_success:
                data = res.json()
                return VendorResponse(
                    success=True,
                    transaction_id=data.get("accountId"),
                    message=data.get("message"),
                    raw_data=data
                )
            else:
                raise VendorIntegrationException(f"Identity service deactivate returned status {res.status_code}: {res.text}")
        except VendorIntegrationException:
            raise
        except Exception as ex:
            logger.error(f"Identity service deactivate failure: {ex}")
            raise VendorIntegrationException(f"Identity service deactivate failure: {str(ex)}") from ex
