import zeep
import logging
from datetime import datetime
from app.config import settings
from app.schemas.workflow import VendorResponse
from app.adapters.exceptions import VendorIntegrationException

logger = logging.getLogger("LegacyHrSoapAdapter")

class LegacyHrSoapAdapter:
    def __init__(self, wsdl_url: str = None, client: zeep.Client = None):
        self.wsdl_url = wsdl_url or f"{settings.legacy_hr_soap_url}/ws?wsdl"
        self._client = client

    def _get_client(self):
        if not self._client:
            try:
                self._client = zeep.Client(wsdl=self.wsdl_url)
            except Exception as e:
                logger.error(f"Failed to load WSDL from {self.wsdl_url}: {e}")
                raise VendorIntegrationException(f"Failed to connect to Legacy HR SOAP service: {e}") from e
        return self._client

    def update_employee_status(self, employee, new_status: str) -> VendorResponse:
        logger.info(f"Calling Legacy HR SOAP service to set employee #{employee.id} to {new_status}")
        try:
            client = self._get_client()
            response = client.service.updateEmployeeStatus(
                employeeId=employee.id,
                systemStatus=new_status,
                department=employee.department or "General",
                effectiveDate=datetime.utcnow().strftime("%Y-%m-%d")
            )
            return VendorResponse(
                success=True,
                transaction_id=getattr(response, "transactionId", f"SOAP-{new_status}-{employee.id}"),
                message=getattr(response, "message", f"Legacy HR record updated to {new_status}"),
                raw_data={"ackCode": getattr(response, "ackCode", "ACK_200")}
            )
        except VendorIntegrationException:
            raise
        except Exception as ex:
            logger.error(f"Legacy HR SOAP invocation error: {ex}")
            raise VendorIntegrationException(f"Legacy HR SOAP invocation error: {str(ex)}") from ex
