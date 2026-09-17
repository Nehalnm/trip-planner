from pydantic import BaseModel, EmailStr
import uuid


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str

    class Config:
        from_attributes = True