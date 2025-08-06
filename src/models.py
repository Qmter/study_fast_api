from pydantic import BaseModel


class ExceptionModel(BaseModel):
    status_code: int
    detail: str
    message: str

class CreateUser(BaseModel):
    username: str
    password: str


class ResponseUser(BaseModel):
    username: str