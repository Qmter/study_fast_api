from pydantic import BaseModel, Field, field_validator, EmailStr
from fastapi import Header
from typing import Optional
from uuid import UUID

class Contact(BaseModel):
    email: EmailStr = Field(...)
    phone: Optional[str] = Field(
        default=None,
        min_length=7,
        max_length=15,
        pattern=r'^[0-9]+$',
        examples=["79001234567", "1234567"],
        description="Номер телефона (только цифры, 7-15 символов)"
    )


class Feedback(BaseModel):
    name: str
    message: str
    contact: Contact

    @field_validator('message')
    def check_message(cls, value):
        if 'бяка' in value:
            raise ValueError("Использование недопустимых слов")

        return value
    


class feedbackResponse(BaseModel):
    message: str
    feedback: Feedback


class ClientResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str | None

class UserResponse(BaseModel):
    client: list[ClientResponse]


class ClientResponse_noid(BaseModel):
    name: str
    email: EmailStr
    phone: str | None


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = Field(None, ge=0)
    is_subscribed: Optional[bool] = Field(None)



class LoginUser(BaseModel):
    username: str
    password: str

class CookieUser(BaseModel):
    username: str
    message: str = "Authentication successful"



class User(BaseModel):
    id: UUID
    username: str
    password: str

class LoginUser2(BaseModel):
    username: str
    password: str


class CommonHeaders(BaseModel):
    user_agent: str
    accept_language: str
