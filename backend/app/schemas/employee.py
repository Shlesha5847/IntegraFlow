from pydantic import BaseModel, EmailStr, Field, ConfigDict
from pydantic.alias_generators import to_camel
from datetime import datetime
from typing import Optional
from app.models.enums import EmployeeStatus

class EmployeeBase(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

    full_name: str = Field(..., max_length=150, description="Employee full name")
    email: EmailStr = Field(..., max_length=150, description="Employee email")
    department: Optional[str] = Field(None, max_length=100, description="Department")
    status: Optional[EmployeeStatus] = EmployeeStatus.ACTIVE

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

    full_name: Optional[str] = Field(None, max_length=150)
    email: Optional[EmailStr] = Field(None, max_length=150)
    department: Optional[str] = Field(None, max_length=100)
    status: Optional[EmployeeStatus] = None

class EmployeeResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

    id: int
    full_name: str
    email: str
    department: Optional[str] = None
    status: EmployeeStatus
    created_at: datetime
