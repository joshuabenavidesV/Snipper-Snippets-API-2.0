from fastapi import FastAPI, HTTPException, Query
import json
from pydantic import BaseModel
from typing import Optional
import os
import bcrypt
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

app = FastAPI() 

FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    raise ValueError("FERNET_KEY not found in .env file")

fernet = Fernet(FERNET_KEY.encode())

def decrypt_snippet(snippet):
    try:
        decrypted_code = fernet.decrypt(snippet["code"].encode()).decode()
    except Exception:
        decrypted_code = snippet["code"]  
    return {
        "id": snippet["id"],
        "language": snippet["language"],
        "code": decrypted_code
    }

def load_data():
    seed_Data = "seedData.json"
    with open(seed_Data, "r") as file:
        data = json.load(file)
    return data

def save_data(data):
    file_name = "data.json"
    with open(file_name, "w") as file:
        json.dump(data, file)

data = load_data()

class Snippet(BaseModel):
    language: str
    code: str

@app.get("/snippets")
def get_all_snippets(lang: Optional[str] = None):
    language = lang
    if language is not None:
        return [
            decrypt_snippet(snippet)
            for snippet in data
            if snippet.get("language", "").lower() == lang.lower()
        ]
    return [decrypt_snippet(snippet) for snippet in data]

@app.get("/snippets/{snippet_id}")
def get_snippets_id(snippet_id: int):
    for snippet in data:
        if snippet.get("id") == snippet_id:
            return decrypt_snippet(snippet)
    return {"error": "Snippet not found"}

@app.post("/snippets")
def create_snippet(snippet: Snippet):
    encrypted_code = fernet.encrypt(snippet.code.encode()).decode()  # decode to string for JSON
    new_snippet = {
        "id": len(data) + 1,
        "language": snippet.language,
        "code": encrypted_code,
    }
    data.append(new_snippet)
    save_data(data)
    return new_snippet

@app.delete("/snippets/{snippet_id}")
def delete_snippet(snippet_id: int):
    global data
    updated_data = []
    found = False
    for snippet in data:
        if snippet.get("id") == snippet_id:
            found = True  
        else:
            updated_data.append(snippet)

    if found == False:
        return {"error": f"Snippet with ID {snippet_id} not found"}
    data = updated_data
    save_data(updated_data)

    return {"message": f"Snippet with ID {snippet_id} deleted successfully"}

class User(BaseModel):
    email: str
    password: str

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

@app.post("/user")
def create_user(user: User):
    user_data = {
        "email": user.email,
        "password": hash_password(user.password)
    }

    # Load existing users if file exists, else empty list
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            users = json.load(f)
    else:
        users = []

    users.append(user_data)

    # Saves updated user list
    with open("users.json", "w") as f:
        json.dump(users, f)

    return {"message": f"User {user.email} created successfully"}

@app.get("/user")
def get_user(email: str = Query(...), password: str = Query(...)): # Query parameters for email and password
    if not os.path.exists("users.json"):# Check if users.json exists
        raise HTTPException(status_code=404, detail="No users found")

    with open("users.json", "r") as f:
        users = json.load(f)

    for user in users:
        if user["email"] == email and bcrypt.checkpw(password.encode(), user["password"].encode()): # Check if email and password match
            # Return user information without password
            return {"You have logged into user ": user["email"]}  

    raise HTTPException(status_code=401, detail="Invalid email or password")
    







