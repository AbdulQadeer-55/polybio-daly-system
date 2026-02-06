from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

@app.get("/api/health")
def health_check():
    return {"status": "active", "system": "PolyBio Markov Engine"}