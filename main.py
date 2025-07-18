from fastapi import FastAPI
import json
from pydantic import BaseModel

app = FastAPI()

def load_data():
    seed_Data = "seedData.json"
    with open(seed_Data, "r") as file:
        data = json.load(file)
    return data

def save_data():
    save_data = "data.json"
    with open(save_data, "w") as file:
        json.dump(data, file)

data = load_data()

class Snippet(BaseModel):
    language: str
    code: str

@app.get("/snippets")
def get_Allsnippets():
    return data

@app.get("/snippets/{snippet_id}")
def get_snippets_id(snippet_id: int):
    for snippet in data:
        if snippet.get("id") == snippet_id:
            return snippet
    return {"error": "Snippet not found"}

@app.post("/snippets")
def create_snippet(snippet: Snippet):
    new_snippet = {
        "id": len(data) + 1,
        "language": snippet.language,
        "code": snippet.code,
    }
    data.append(new_snippet)
    save_data()
    return new_snippet
    




