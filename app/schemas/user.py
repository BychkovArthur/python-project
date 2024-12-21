from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    role: str  # 'admin', 'analyst', 'partner'
    model_config = ConfigDict(from_attributes=True)


class UserIn(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_is_not_blank(cls, value):
        if not value.strip():
            raise ValueError("Password field can't be blank!")
        return value


class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


class ChangePasswordIn(BaseModel):
    old_password: str
    new_password: str

    @field_validator("old_password")
    @classmethod
    def old_password_is_not_blank(cls, value):
        if not value.strip():
            raise ValueError("Old password field can't be blank!")
        return value

    @field_validator("new_password")
    @classmethod
    def new_password_is_not_blank(cls, value):
        if not value.strip():
            raise ValueError("New password field can't be blank!")
        return value
