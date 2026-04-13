from pydantic import BaseModel
from typing import Optional, Dict

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    email: str
    name: Optional[str] = None
    permissions: Dict[str, bool] = {}

class UserOut(BaseModel):
    email: str
    role: str
    name: Optional[str] = None
    permissions: Dict[str, bool] = {}