import os
import json
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Character schema
class Character(BaseModel):
    name: str
    age: int
    favorite_food: str
    quote: str

# Quote schema
class Quote(BaseModel):
    name: str
    quote: str

# Function to save the character as a new row to CSV file
def save_character(name, age, favorite_food, quote):
    file_name = "characters.csv"

    # Check if file exists and create if necessary
    if not os.path.exists(file_name) or os.stat(file_name).st_size == 0:
        df = pd.DataFrame(columns=["name", "age", "favorite_food", "quote"])
    else:
        df = pd.read_csv(file_name)

    # Append new character
    df.loc[len(df)] = [name, age, favorite_food, quote]
    df.to_csv(file_name, index=False)

# Function to save the character's quote as a new row to CSV file
def save_quote(name, quote):
    file_name = "quotes.csv"

    # Check if file exists and create if necessary
    if not os.path.exists(file_name) or os.stat(file_name).st_size == 0:
        df = pd.DataFrame(columns=["name", "quote"])
    else:
        df = pd.read_csv(file_name)

    # Append new quote
    df.loc[len(df)] = [name, quote]
    df.to_csv(file_name, index=False)

# POST: Create a character route
@app.post("/create_character")
async def create_character(data: Character):
    save_character(data.name, data.age, data.favorite_food, data.quote)
    save_quote(data.name, data.quote)
    return {
        "msg": "Character Created!",
        "name": data.name,
        "age": data.age,
        "favorite_food": data.favorite_food,
        "quote": data.quote
    }

# POST: Add a new quote
@app.post("/add_quote")
async def add_quote(data: Quote):
    file_name = "quotes.csv"

    # Ensure character exists before adding a quote
    char_file = "characters.csv"
    if os.path.exists(char_file):
        df_chars = pd.read_csv(char_file)
        if data.name not in df_chars["name"].values:
            raise HTTPException(status_code=404, detail="Character not found.")

    # Save the quote
    save_quote(data.name, data.quote)

    return {"msg": "Quote added!", "name": data.name, "quote": data.quote}

# GET: Get all characters route
@app.get("/characters")
def get_characters():
    file_name = "characters.csv"
    
    # If the file does not exist, return an empty list
    if not os.path.exists(file_name):
        return {"msg": "No characters found."}

    df = pd.read_csv(file_name).dropna()
    return json.loads(df.to_json(orient="records"))

# GET: Get a character by name
@app.get("/characters/{name}")
async def get_character(name: str):
    file_name = "characters.csv"

    if not os.path.exists(file_name):
        return {"msg": "Character not found."}

    df = pd.read_csv(file_name).dropna()
    df = df[df["name"].str.contains(name, na=False, case=False)]

    if df.empty:
        return {"msg": "Character not found."}

    return json.loads(df.to_json(orient="records"))

# GET: Get a random quote route
@app.get("/quote")
def get_quote():
    file_name = "quotes.csv"

    if not os.path.exists(file_name):
        return {"msg": "No quotes available."}

    df = pd.read_csv(file_name).dropna()
    
    if df.empty:
        return {"msg": "No quotes available."}
    
    df = df.drop(columns=['name'])
    df = df.sample()
    
    return json.loads(df.to_json(orient="records"))
