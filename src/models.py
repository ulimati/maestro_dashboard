from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime

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

# Nový model pro výsledky testů
class TestResultCreate(BaseModel):
    test_name: str
    status: str  # "passed" nebo "failed"
    duration: float
    platform: str  # "android" nebo "ios"
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)