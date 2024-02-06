from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


class SuccessResponse(BaseModel):
    status: bool
    message: str
