from pydantic import BaseModel, Field, field_validator
import re

class CommonHeaders(BaseModel):
    user_agent: str = Field(..., alias="User-Agent")
    accept_language: str = Field(..., alias="Accept-Language")
    
    @field_validator("accept_language")
    @classmethod
    def validate_accept_language(cls, v: str) -> str:
        pattern = r'^[a-z]{2}(-[A-Z]{2})?(,[a-z]{2}(-[A-Z]{2})?;q=[01](\.\d{1,3})?)*$|^[a-z]{2}(-[A-Z]{2})?$'
        if not re.match(pattern, v) and v != "*":
            raise ValueError("Неверный формат Accept-Language")
        return v
    
    class Config:
        populate_by_name = True

class LoginRequest(BaseModel):
    username: str
    password: str