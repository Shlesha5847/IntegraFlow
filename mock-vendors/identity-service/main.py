from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("identity-service")

app = FastAPI(title="Mock Identity Service", version="1.0.0")

class CreateAccountRequest(BaseModel):
    employeeId: int
    fullName: str
    email: str
    department: Optional[str] = None

@app.post("/api/accounts")
def create_account(req: CreateAccountRequest):
    logger.info(f"Provisioning identity account for employee #{req.employeeId}: {req.fullName} ({req.email})")
    account_id = f"IDN-{req.employeeId}"
    return {
        "accountId": account_id,
        "message": f"Identity account successfully provisioned for {req.fullName} (TxID: {account_id})",
        "status": "CREATED",
        "email": req.email
    }

@app.delete("/api/accounts/{employee_id}")
def deactivate_account(employee_id: int):
    logger.info(f"Deactivating identity account for employee #{employee_id}")
    account_id = f"IDN-{employee_id}"
    return {
        "accountId": account_id,
        "message": f"Identity account successfully deactivated for employee #{employee_id} (TxID: {account_id})",
        "status": "DEACTIVATED"
    }

@app.get("/health")
def health():
    return {"status": "UP"}
