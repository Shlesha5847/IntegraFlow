from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="", tags=["Employees"])
employee_service = EmployeeService()

@router.get("/employees", response_model=List[EmployeeResponse])
@router.get("/api/employees", response_model=List[EmployeeResponse], include_in_schema=False)
def get_all_employees(db: Session = Depends(get_db)):
    return employee_service.get_all_employees(db)

@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
@router.get("/api/employees/{employee_id}", response_model=EmployeeResponse, include_in_schema=False)
def get_employee_by_id(employee_id: int, db: Session = Depends(get_db)):
    return employee_service.get_employee_by_id(db, employee_id)

@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
@router.post("/api/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_employee(employee_in: EmployeeCreate, db: Session = Depends(get_db)):
    return employee_service.create_employee(db, employee_in)

@router.put("/employees/{employee_id}", response_model=EmployeeResponse)
@router.put("/api/employees/{employee_id}", response_model=EmployeeResponse, include_in_schema=False)
def update_employee(employee_id: int, employee_in: EmployeeUpdate, db: Session = Depends(get_db)):
    return employee_service.update_employee(db, employee_id, employee_in)

@router.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/api/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT, include_in_schema=False)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee_service.delete_employee(db, employee_id)
    return None
