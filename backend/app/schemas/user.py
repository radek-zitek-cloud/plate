from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# Properties to receive via API on update
class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    full_name: str | None = None
    password: str | None = None
    is_active: bool | None = None


# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


class Token(BaseModel):
    """Response schema for login endpoint."""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Data structure of JWT token payload."""
    sub: str | None = None  # subject - typically user ID


class PasswordChange(BaseModel):
    """Schema for password change request."""
    current_password: str
    new_password: str