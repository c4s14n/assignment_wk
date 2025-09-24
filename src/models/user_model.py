from pydantic import BaseModel


class UserModel(BaseModel):
    """Schema for validating User API responses in tests."""
    id: int
    name: str
    username: str
    email: str
    phone: str
