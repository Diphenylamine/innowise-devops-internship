import random
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response

app = FastAPI()

SERVER_NUMBER = random.randint(1, 1000)

@app.get("/", response_class=HTMLResponse)
def index():
    return Path("index.html").read_text(encoding="utf-8")

@app.get("/style.css")
def style():
    return Response(Path("style.css").read_text(encoding="utf-8"), media_type="text/css")

@app.get("/api/server-number")
def server_number():
    return {"number": SERVER_NUMBER}