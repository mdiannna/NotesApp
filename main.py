from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from fastapi import Request
from pydantic import BaseModel

# from bson import ObjectId
# import pymongo
# from pymongo import AsyncMongoClient
# from pymongo import ReturnDocument
# from pymongo.server_api import ServerApi


app = FastAPI()
templates = Jinja2Templates("templates")


UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")


# client = AsyncMongoClient(os.environ["MONGODB_URL"],server_api=pymongo.server_api.ServerApi(version="1", strict=True,deprecation_errors=True))
# db = client.college
# student_collection = db.get_collection("students")

class Note(BaseModel):
    text: str
    disabled: bool | None = None

class NoteRequest(BaseModel):
    note_text: str | None = None

# placeholder instead of the database
notes = ["note1", "note2", "note4"]

@app.get("/")
async def read_root(request:Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/notes")
async def get_notes(request:Request):
    # return a placeholder for now
    return notes

@app.post("/api/notes/create")
async def create_note(request: NoteRequest):
    print("request to create note")
    print(request.note_text)
    notes.append(request.note_text)
    #TODO: create note and (fake) database or use mongo with motor
    return "note created succesful"