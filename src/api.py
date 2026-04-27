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
from src.db import sessions, users, test_results, db   # ← přidáno: db
import src.data_provider as data_provider

app = FastAPI(title="Maestro API", version="2.0")

@app.get("/")
def home():
    return {"status": "API is running", "message": "Go to /api/metrics for data"}

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
def me():
    return UserOut(
        email="admin@maestro.local",
        role="admin",
        name="Admin Uživatel",
        permissions={"all": True}
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
def dashboard_summary():
    return {
        "email": "admin@maestro.local",
        "role": "admin",
        "permissions": {"all": True}
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
# TEST RESULTS
# -------------------------

@app.post("/api/test-results")
def save_test_result(result: TestResultCreate):
    new_result = result.model_dump()
    test_results.insert_one(new_result)
    return {"status": "success", "message": "Test result saved."}

@app.get("/api/metrics")
def get_metrics(platform: str = "android"):
    return data_provider.get_metrics_for_platform(platform)

@app.post("/api/login")
async def api_login(request: LoginRequest):
    user = verify_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({
        "sub": user["email"],
        "email": user["email"],
        "role": user.get("role"),
        "name": user.get("name"),
    })
    
    return {
        "access_token": token,
        "email": user["email"],
        "name": user.get("name", ""),
        "role": user.get("role", "viewer"),
        "permissions": user.get("permissions", {
            "view_details": True,
            "expand_graphs": True,
            "view_summary": True,
        }),
    }

@app.get("/api/test-results")
def get_test_results(platform: str = "android", date: str = None):
    from datetime import datetime, timedelta
    query = {"platform": platform}
    if date:
        start = datetime.strptime(date, "%Y-%m-%d")
        end = start + timedelta(days=1)
        query["timestamp"] = {"$gte": start, "$lt": end}
    results = list(test_results.find(query, {"_id": 0}))
    return {"results": results}

@app.get("/api/test-dates")
def get_test_dates(platform: str = "android"):
    results = list(test_results.find({"platform": platform}, {"timestamp": 1, "_id": 0}))
    dates = set()
    for r in results:
        ts = r.get("timestamp")
        if ts:
            formatted = ts.strftime("%Y-%m-%d")
            dates.add(formatted)
    return {"dates": list(dates)}

# -------------------------
# DEVICE LOGS ← NOVÉ
# -------------------------

@app.post("/api/device-logs")
def save_device_log(payload: dict):
    """Uloží console log z jednoho test runu do kolekce device_logs."""
    db["device_logs"].update_one(
        {"run_id": payload["run_id"]},
        {"$set": payload},
        upsert=True
    )
    return {"status": "success", "message": f"Device log saved: {payload['run_id']}"}

@app.get("/api/device-logs")
def get_device_logs(platform: str = None, status: str = None):
    """Vrátí seznam device logů, volitelně filtrovaný podle platformy nebo statusu."""
    query = {}
    if platform:
        query["platform"] = platform
    if status:
        query["status"] = status
    logs = list(db["device_logs"].find(query, {"_id": 0, "log_entries": 0}))
    return {"logs": logs}