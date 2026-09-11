from sqlalchemy import Column, BigInteger, String, Enum as SQLEnum, DateTime
from datetime import datetime
from app.database import Base
from app.models.enums import EmployeeStatus

class Employee(Base):
    __tablename__ = "employee"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    department = Column(String(100), nullable=True)
    status = Column(SQLEnum(EmployeeStatus, name="employee_status_enum", native_enum=False), nullable=False, default=EmployeeStatus.ACTIVE)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
