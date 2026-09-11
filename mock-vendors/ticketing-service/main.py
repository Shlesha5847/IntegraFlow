from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ticketing-service")

app = FastAPI(title="Mock Ticketing Service", version="1.0.0")

class CreateTicketRequest(BaseModel):
    employeeId: int
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "MEDIUM"

@app.post("/api/tickets")
def create_ticket(req: CreateTicketRequest):
    logger.info(f"Creating IT ticket for employee #{req.employeeId}: {req.title}")
    ticket_id = f"TCK-{1000 + req.employeeId}"
    return {
        "ticketId": ticket_id,
        "message": f"IT ticket {ticket_id} successfully created: {req.title} (TxID: {ticket_id})",
        "status": "OPEN",
        "employeeId": req.employeeId,
        "title": req.title
    }

@app.put("/api/tickets/close-all/{employee_id}")
def close_all_tickets(employee_id: int):
    logger.info(f"Closing all IT tickets for employee #{employee_id}")
    tx_id = f"CLOSE-{employee_id}"
    return {
        "closedTicketsCount": 3,
        "message": f"All IT tickets closed for employee #{employee_id} (TxID: {tx_id})",
        "status": "CLOSED"
    }

@app.get("/health")
def health():
    return {"status": "UP"}
