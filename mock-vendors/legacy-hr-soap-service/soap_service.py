from spyne import Application, rpc, ServiceBase, Integer, Unicode, ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("legacy-hr-soap-service")

class UpdateEmployeeStatusResponse(ComplexModel):
    __namespace__ = "http://integraflow.com/legacyhr"
    ackCode = Unicode
    message = Unicode
    transactionId = Unicode
    timestamp = Unicode

class LegacyHrSoapService(ServiceBase):
    @rpc(Integer, Unicode, Unicode, Unicode, _returns=UpdateEmployeeStatusResponse)
    def updateEmployeeStatus(ctx, employeeId, systemStatus, department, effectiveDate):
        logger.info(f"Received SOAP updateEmployeeStatus: employeeId={employeeId}, status={systemStatus}, dept={department}, date={effectiveDate}")
        tx_id = f"SOAP-{systemStatus}-{employeeId}"
        return UpdateEmployeeStatusResponse(
            ackCode="ACK_200",
            message=f"Legacy HRIS record updated: Employee #{employeeId} is now marked as {systemStatus} (TxID: {tx_id})",
            transactionId=tx_id,
            timestamp=datetime.utcnow().isoformat()
        )

application = Application(
    [LegacyHrSoapService],
    tns="http://integraflow.com/legacyhr",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11()
)

wsgi_application = WsgiApplication(application)

if __name__ == "__main__":
    logger.info("Starting Legacy HR Spyne SOAP Service on port 8081...")
    server = make_server("0.0.0.0", 8081, wsgi_application)
    server.serve_forever()
