import streamlit as st
from pymongo import MongoClient
import certifi
import bcrypt

@st.cache_resource
def get_client():
    return MongoClient(
        st.secrets["MONGO_URI"],
        tlsCAFile=certifi.where()
    )

client = get_client()
db = client["maestro_db"]
users = db["users"]

def get_user_by_email(email):
    return users.find_one({"email": email})

def get_all_users(limit=100):
    return list(users.find({}, {"_id": 0}).limit(limit))

def get_role(email):
    user = users.find_one({"email": email}, {"role": 1})
    return user["role"] if user else None

def verify_user(email, password):
    user = users.find_one({"email": email})
    if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
        return user
    return None