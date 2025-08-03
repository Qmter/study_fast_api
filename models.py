from pydantic import BaseModel, Field
from datetime import datetime, date


class CreateTodo(BaseModel):
    title: str = Field(..., max_length=50)
    description: str = Field(..., max_length=255)

class ReturnTodo(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime
    completed_at: datetime | None
