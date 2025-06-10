import re
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError, ConfigDict
from .entity import BaseEntity

class CustomerData(BaseModel):
   model_config = ConfigDict(
      json_schema_extra={
         "example": {
            "name": "John Doe",
            "email": "john.doe@example.com"
         }
      }
   )
   
   name: str = Field(
      ..., 
      min_length=1, 
      max_length=100,
      description="Customer's full name"
   )
   email: EmailStr = Field(
      ..., 
      description="Customer's email address"
   )
   
   @field_validator('name')
   @classmethod
   def validate_name(cls, v: str) -> str:
      if not v or not v.strip():
         raise ValueError('Name cannot be empty or whitespace only')
      
      v = v.strip()
      
      if not re.match(r"^[a-zA-ZÀ-ÿ\s\-'\.]+$", v):
         raise ValueError('Name contains invalid characters')
      
      return v
   
   @field_validator('email')
   @classmethod
   def validate_email_domain(cls, v: EmailStr) -> EmailStr:
      email_str = str(v)
      
      if email_str.count('@') != 1:
         raise ValueError('Invalid email format')
      
      return v


class Customer(BaseEntity):   
   def __init__(self, name: str, email: str):
      self.name = name
      self.email = email
   
   @property
   def name(self) -> str:
      return self._name
   
   @name.setter
   def name(self, value: str) -> None:
      self._name = value

   @property
   def email(self) -> str:
      return self._email
   
   @email.setter
   def email(self, value: str) -> None:
      self._email = value

   def __str__(self) -> str:
      return f"{self.name} <{self.email}>"
   
   def to_serializable(self) -> CustomerData:
      return CustomerData(
         name=self.name,
         email=self.email
      )
   
   @classmethod
   def from_serializable(cls, data: CustomerData) -> 'Customer':
      return cls(
         name=data.name,
         email=str(data.email)
      )
   
   @classmethod
   def from_dict(cls, data: dict) -> 'Customer':
      return cls.from_serializable(CustomerData(**data))
   
   def to_dict(self) -> dict:
      return self.to_serializable().model_dump()
   
   def to_json(self) -> str:
      return self.to_serializable().model_dump_json()
   
   @classmethod
   def from_json(cls, json_str: str) -> 'Customer':
      return cls.from_serializable(CustomerData.model_validate_json(json_str))
   
   @classmethod
   def validate_data(cls, data: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
      try:
         CustomerData(**data)
         return None
      except ValidationError as e:
         return [
            {
               "field": error.get("loc", ["unknown"])[0] if error.get("loc") else "unknown",
               "message": error.get("msg", "Unknown error"),
               "input": error.get("input", data)
            }
            for error in e.errors()
         ]
   
   @classmethod
   def validate_and_throw(cls, data: Dict[str, Any]) -> None:
      CustomerData(**data)
   
   def validate(self) -> Optional[List[Dict[str, Any]]]:
      return self.validate_data({
         "name": self.name,
         "email": self.email
      })