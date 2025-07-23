from fastapi import FastAPI
import json
from pydantic import BaseModel
from typing import Optional
from cryptography.fernet import Fernet
import os


app = FastAPI()

key_file_path = "secret.key"
if not os.path.exists(key_file_path):
    key = Fernet.generate_key()
    with open(key_file_path, "wb") as key_file:
        key_file.write(key)
else:
    with open(key_file_path, "rb") as key_file:
        key = key_file.read()

fernet = Fernet(key)

def decrypt_snippet(snippet):
    try:
        decrypted_code = fernet.decrypt(snippet["code"].encode()).decode()
    except Exception:
        decrypted_code = snippet["code"]  # fallback to plain text if not encrypted
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







