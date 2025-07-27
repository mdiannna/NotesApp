from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from fastapi import Request
from pydantic import BaseModel, Field

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
# from bson import ObjectId
# import pymongo
# from pymongo import AsyncMongoClient
# from pymongo import ReturnDocument
# from pymongo.server_api import ServerApi


app = FastAPI()
templates = Jinja2Templates("templates")

# MongoDB config
MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client.testdb
collection = db.notes


UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")



# client = AsyncMongoClient(os.environ["MONGODB_URL"],server_api=pymongo.server_api.ServerApi(version="1", strict=True,deprecation_errors=True))
# db = client.college
# student_collection = db.get_collection("students")

# Pydantic model
class Note(BaseModel):
    text: str
    author: str = ""
    # disabled: bool | None = None

class NoteOut(Note):
    id: str = Field(default_factory=str)

# Helpers
def note_helper(note) -> dict:
    return {
        "id": str(note["_id"]),
        "text": note.get("text", ""),
        "author": note.get("author", ""),
    }

class NoteRequest(BaseModel):
    text: str | None = None
    author: str | None = None

# placeholder instead of the database
notes = ["note1", "note2", "note4"]

@app.get("/")
async def read_root(request:Request):
    return templates.TemplateResponse("index.html", {"request": request})


# @app.get("/api/notes")
# async def get_notes(request:Request):
#     # return a placeholder for now
#     return notes

# @app.post("/api/notes/create")
# async def create_note(request: NoteRequest):
#     print("request to create note")
#     print(request.note_text)
#     notes.append(request.note_text)
#     #TODO: create note and (fake) database or use mongo with motor
#     return "note created succesful"


# GET all notes
@app.get("/api/notes", response_model=list[NoteOut])
async def get_notes():
    notes_cursor = collection.find()
    notes = []
    async for note in notes_cursor:
        notes.append(note_helper(note))
    return notes

# POST create a note
@app.post("/api/notes/create", response_model=NoteOut)
async def create_note(request: NoteRequest):
    result = await collection.insert_one(request.dict())
    new_note = await collection.find_one({"_id": result.inserted_id})
    return note_helper(new_note)