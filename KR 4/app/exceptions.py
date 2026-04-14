from fastapi import HTTPException
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str
    status_code: int
    error_type: str

class CustomExceptionA(HTTPException):
    def __init__(self, detail: str = "Custom Error A", status_code: int = 400):
        super().__init__(
            status_code=status_code,
            detail=detail
        )

class CustomExceptionB(HTTPException):
    def __init__(self, detail: str = "Custom Error B", status_code: int = 404):
        super().__init__(
            status_code=status_code,
            detail=detail
        )