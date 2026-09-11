from sqlalchemy.orm import Session
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.adapters.exceptions import ResourceNotFoundException, DuplicateResourceException
import logging

logger = logging.getLogger("EmployeeService")

class EmployeeService:
    def get_all_employees(self, db: Session):
        return db.query(Employee).order_by(Employee.id.asc()).all()

    def get_employee_by_id(self, db: Session, employee_id: int):
        emp = db.query(Employee).filter(Employee.id == employee_id).first()
        if not emp:
            raise ResourceNotFoundException(f"Employee not found with id: {employee_id}")
        return emp

    def create_employee(self, db: Session, employee_in: EmployeeCreate):
        existing = db.query(Employee).filter(Employee.email == employee_in.email).first()
        if existing:
            raise DuplicateResourceException(f"Employee with email {employee_in.email} already exists")

        emp = Employee(
            full_name=employee_in.full_name,
            email=employee_in.email,
            department=employee_in.department,
            status=employee_in.status
        )
        db.add(emp)
        db.commit()
        db.refresh(emp)
        return emp

    def update_employee(self, db: Session, employee_id: int, employee_in: EmployeeUpdate):
        emp = self.get_employee_by_id(db, employee_id)
        if employee_in.email and employee_in.email != emp.email:
            existing = db.query(Employee).filter(Employee.email == employee_in.email).first()
            if existing:
                raise DuplicateResourceException(f"Employee with email {employee_in.email} already exists")
            emp.email = employee_in.email

        if employee_in.full_name is not None:
            emp.full_name = employee_in.full_name
        if employee_in.department is not None:
            emp.department = employee_in.department
        if employee_in.status is not None:
            emp.status = employee_in.status

        db.commit()
        db.refresh(emp)
        return emp

    def delete_employee(self, db: Session, employee_id: int):
        emp = self.get_employee_by_id(db, employee_id)
        db.delete(emp)
        db.commit()
