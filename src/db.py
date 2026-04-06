import certifi
from pymongo import MongoClient

CONNECTION_STRING = "mongodb+srv://maestro_user:Heslo1234@cluster0.9wexwdh.mongodb.net/?appName=Cluster0"

client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
db = client["maestro_db"]
users = db["users"]

def get_user_by_email(email):
    return users.find_one({"email": email})

def get_all_users():
    return list(users.find())

def get_role(email):
    user = get_user_by_email(email)
    if user:
        return user["role"]
    return None

def verify_user(email, password):
    user = users.find_one({"email": email, "password": password})
    return user
