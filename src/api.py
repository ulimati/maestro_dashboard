from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials
from src.auth import verify_user
from src.models import LoginRequest, TokenResponse, UserOut, TestResultCreate
from src.dependencies import (
    create_access_token,
    get_current_user,
    require_role,
    security
)
from src.db import sessions, users, test_results
import src.data_provider as data_provider

app = FastAPI(title="Maestro API", version="2.0")

# CORS pro Lovable
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# PUBLIC
# -------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    user = verify_user(data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({
        "sub": user["email"],
        "email": user["email"],
        "role": user.get("role"),
        "name": user.get("name"),
        "permissions": user.get("permissions", {})
    })
    
    return TokenResponse(
        access_token=token,
        role=user.get("role"),
        email=user["email"],
        name=user.get("name"),
        permissions=user.get("permissions", {})
    )

# -------------------------
# PROTECTED — any logged user
# -------------------------

@app.get("/me", response_model=UserOut)
def me(user: dict = Depends(get_current_user)):
    return UserOut(
        email=user["email"],
        role=user["role"],
        name=user.get("name"),
        permissions=user.get("permissions", {})
    )

@app.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user: dict = Depends(get_current_user)
):
    sessions.insert_one({
        "token": credentials.credentials,
        "email": user["email"],
        "invalidated": True
    })
    return {"message": "Logged out successfully"}

@app.get("/dashboard/summary")
def dashboard_summary(user: dict = Depends(get_current_user)):
    return {
        "email": user.get("email"),
        "role": user["role"],
        "permissions": user.get("permissions", {})
    }

# -------------------------
# PROTECTED — admin only
# -------------------------

@app.get("/admin/users")
def list_users(user: dict = Depends(require_role("admin"))):
    all_users = list(users.find({}, {"password": 0, "password_hash": 0}))
    for u in all_users:
        u["_id"] = str(u["_id"])
    return all_users

@app.delete("/admin/users/{email}")
def delete_user(email: str, user: dict = Depends(require_role("admin"))):
    result = users.delete_one({"email": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {email} deleted"}

# -------------------------
# TEST RESULTS (Pro Lovable a Test Runner)
# -------------------------

@app.post("/api/test-results")
def save_test_result(result: TestResultCreate):
    """Endpoint pro test runner na uložení výsledku do MongoDB."""
    # model_dump() je moderní způsob v Pydantic v2 (nahrazuje dict())
    new_result = result.model_dump() 
    test_results.insert_one(new_result)
    return {"status": "success", "message": "Test result saved."}

@app.get("/api/metrics")
def get_metrics(platform: str = "android"):
    """Endpoint pro Lovable na získání dat pro grafy a karty."""
    return data_provider.get_metrics_for_platform(platform)