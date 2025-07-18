from fastapi import FastAPI
import json
from pydantic import BaseModel
from typing import Optional


app = FastAPI()

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
    # If the user provided a language filter in the URL
    language = lang
    if language is not None:
        # Create a new list to store matching snippets
        filtered_snippets = []

        # Go through each snippet in the data list
        for snippet in data:
            # Get the language from the snippet (default to empty string if missing)
            snippet_language = snippet.get("language", "")

            # Compare it to the user's input (case-insensitive)
            if snippet_language.lower() == language.lower():
                # If it matches, add this snippet to the results list
                filtered_snippets.append(snippet)

        # Return the filtered list
        return filtered_snippets

    # If no language filter was provided, return all snippets
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







