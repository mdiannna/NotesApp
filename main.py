from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from fastapi import Request, HTTPException
from pydantic import BaseModel, Field

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId


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
    id: str | None = None
    text: str | None = None
    author: str | None = None

# placeholder instead of the database
notes = ["note1", "note2", "note4"]

@app.get("/")
async def read_root(request:Request):
    notes_cursor = collection.find()
    notes = []
    async for note in notes_cursor:
        notes.append(note_helper(note))
    return templates.TemplateResponse("view_notes.html", {"request": request, "notes":notes})


@app.get("/add_note")
async def add_note(request:Request):
    return templates.TemplateResponse("add_note.html", {"request": request})


@app.get("/view_note/{note_id}")
async def add_note(request:Request, note_id:str):
    return templates.TemplateResponse("view_note.html", {"request": request, "noteId":note_id})


# GET all notes
@app.get("/api/notes", response_model=list[NoteOut])
async def get_notes():
    notes_cursor = collection.find()
    notes = []
    async for note in notes_cursor:
        notes.append(note_helper(note))
    return notes

# GET one note
@app.get("/api/notes/{note_id}", response_model=dict)
async def get_one_note(note_id:str):

    if not ObjectId.is_valid(note_id):
        raise HTTPException(status_code=400, detail="invalid note ID format")
    
    note = await collection.find_one({"_id": ObjectId(note_id)})
    return note_helper(note)

# POST create a note
@app.post("/api/notes/create", response_model=NoteOut)
async def create_note(request: NoteRequest):
    result = await collection.insert_one(request.dict())
    new_note = await collection.find_one({"_id": result.inserted_id})
    return note_helper(new_note)



@app.delete("/api/notes/{note_id}", response_model=dict)
async def delete_note(note_id:str):
    if not ObjectId.is_valid(note_id):
        raise HTTPException(status_code=400, detail="invalid note ID format")
    
    result = await collection.delete_one({"_id": ObjectId(note_id)})

    if result.deleted_count==1:
        return {"message": "Note deleted successfully"}
    # else
    raise HTTPException(status_code=404, detail="Note not found")


# POST update note
@app.post("/api/notes/update", response_model=NoteOut)
async def update_note(request: NoteRequest):
    print("update note request:")
    print(request.dict())

    note_id = request.id
    print("note_id:", note_id)
    
    if not ObjectId.is_valid(note_id):
        raise HTTPException(status_code=400, detail="Invalid note ID.")

    update_data = request.dict()
    update_data.pop("id")  # Don't try to update the _id field

    existing_note = await collection.find_one({"_id": ObjectId(note_id)})
    
    if not existing_note:
        raise HTTPException(status_code=404, detail="Note not found.")
    
    result = await collection.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": update_data}
    )

    # if result.modified_count == 0:
    #     raise HTTPException(status_code=404, detail="No changes made.")

    updated_note = await collection.find_one({"_id": ObjectId(note_id)})
    return note_helper(updated_note)
