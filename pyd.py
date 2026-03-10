from pydantic import BaseModel, Field, EmailStr, model_validator
from typing import List, Optional


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9]+$")
    email: EmailStr
    password: str = Field(min_length=8, pattern=r"^[a-zA-Z0-9]+$")
    full_name: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=18, le=120)
    is_active: bool = True


class User(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    age: Optional[int] = None


class ItemCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    price: float = Field(ge=0.01, le=1000000)
    tax: float = Field(
        default=0.0, ge=0, le=100, description="in percents (from 0 to 100)"
    )
    tags: Optional[List[str]] = Field(default=None, max_items=5)
    in_stock: bool
    quantity: Optional[int] = Field(default=None, ge=0, le=1000)

    @model_validator(mode="after")
    def check_quantity_in_stock(self):
        if not self.in_stock:
            self.quantity = 0
        return self


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    total_price: float
    tags: Optional[List[str]] = None
    in_stock: bool
    quantity: int


class UnfilteredUsers(BaseModel):
    name: str
    age: int
    active: bool


class Filters(BaseModel):
    min_age: Optional[int] = Field(ge=0, le=150)
    max_age: Optional[int] = Field(ge=0, le=150)
    active_only: Optional[bool] = None

    @model_validator(mode="after")
    def check_age_range(cls, values):
        min_age = values.min_age
        max_age = values.max_age
        if min_age is not None and max_age is not None and min_age > max_age:
            raise ValueError("min_age must be < or == max_age")
        return values


class Request(BaseModel):
    users: List[UnfilteredUsers] = Field(..., max_items=100)
    filters: Filters


class Response(BaseModel):
    total_input: int
    filtered_count: int
    filtered_users: List[UnfilteredUsers]
    applied_filters: Filters


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=18, le=120)
    is_active: Optional[bool] = None
