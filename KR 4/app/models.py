from pydantic import BaseModel, EmailStr, constr, conint, Field, ConfigDict
from typing import Optional

class ProductBase(BaseModel):
    title: str
    price: float
    count: int

class ProductCreate(ProductBase):
    pass

class ProductInDB(ProductBase):
    id: int
    description: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserValidation(BaseModel):
    username: str
    age: conint(gt = 18)
    email: EmailStr
    password: constr(min_length = 6, max_length = 10)
    phone: Optional[str] = Field(default="Unknown")