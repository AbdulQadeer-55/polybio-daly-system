from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import SimulationRequest, SimulationResponse
from app.engine import PolyBioEngine

app = FastAPI(title="PolyBio DALY Model API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = PolyBioEngine()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.post("/api/simulate", response_model=SimulationResponse)
async def simulate(request: SimulationRequest):
    result = engine.run_simulation(request.dict())
    return result

@app.get("/api/health")
async def health_check():
    return {"status": "active", "system": "PolyBio Markov Engine"}