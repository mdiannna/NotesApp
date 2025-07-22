from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from fastapi import Request

app = FastAPI()
templates = Jinja2Templates("templates")


UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")




@app.get("/")
async def read_root(request:Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/notes")
async def get_notes(request:Request):
    # return a placeholder for now
    return ["note1", "note2", "note4"]