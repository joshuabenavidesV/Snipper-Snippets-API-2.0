from fastapi import FastAPI
import json
app = FastAPI()

seed_Data = "seedData.json"
with open(seed_Data, "r") as file:
    data = json.load(file)
    
@app.get("/snippets")
def get_Allsnippets():
    return data

@app.get("/snippets/{snippet_id}")
def get_snippets_id(snippet_id: int):
    for snippet in data:
        if snippet.get("id") == snippet_id:
            return snippet
    return {"error": "Snippet not found"}




