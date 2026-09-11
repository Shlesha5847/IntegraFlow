import httpx
import logging
from app.config import settings
from app.schemas.workflow import VendorResponse
from app.adapters.exceptions import VendorIntegrationException

logger = logging.getLogger("TicketingRestAdapter")

class TicketingRestAdapter:
    def __init__(self, base_url: str = None, client: httpx.Client = None):
        self.base_url = base_url or settings.ticketing_service_url
        self.client = client or httpx.Client(timeout=10.0)

    def create_onboarding_tickets(self, employee) -> VendorResponse:
        url = f"{self.base_url}/api/tickets"
        payload = {
            "employeeId": employee.id,
            "title": f"Onboarding IT Setup for {employee.full_name}",
            "description": f"Provision laptop, monitors, and security badge for {employee.full_name} ({employee.department})",
            "priority": "HIGH"
        }
        logger.info(f"Calling Ticketing REST service at {url} for employee #{employee.id}")
        try:
            res = self.client.post(url, json=payload)
            if res.is_success:
                data = res.json()
                return VendorResponse(
                    success=True,
                    transaction_id=data.get("ticketId"),
                    message=data.get("message"),
                    raw_data=data
                )
            else:
                raise VendorIntegrationException(f"Ticketing service returned status {res.status_code}: {res.text}")
        except VendorIntegrationException:
            raise
        except Exception as ex:
            logger.error(f"Ticketing service communication failure: {ex}")
            raise VendorIntegrationException(f"Ticketing service communication failure: {str(ex)}") from ex

    def close_all_tickets(self, employee) -> VendorResponse:
        url = f"{self.base_url}/api/tickets/close-all/{employee.id}"
        logger.info(f"Calling Ticketing REST service at {url} to close tickets for employee #{employee.id}")
        try:
            res = self.client.put(url)
            if res.is_success:
                data = res.json()
                tx_id = f"CLOSE-{employee.id}"
                return VendorResponse(
                    success=True,
                    transaction_id=tx_id,
                    message=data.get("message"),
                    raw_data=data
                )
            else:
                raise VendorIntegrationException(f"Ticketing service close returned status {res.status_code}: {res.text}")
        except VendorIntegrationException:
            raise
        except Exception as ex:
            logger.error(f"Ticketing service close failure: {ex}")
            raise VendorIntegrationException(f"Ticketing service close failure: {str(ex)}") from ex
