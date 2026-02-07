from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
# Absolute imports
from app.schemas import SimulationRequest, SimulationResponse
from app.engine import PolyBioEngine

app = FastAPI(title="PolyBio DALY Model API")

# --- CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engine
engine = PolyBioEngine()

# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- ROOT ROUTE (THE FIX) ---
@app.get("/")
async def read_root():
    """
    Serves the dashboard HTML when visiting the root URL.
    """
    return FileResponse("static/index.html")

# --- API ROUTES ---
@app.post("/api/simulate", response_model=SimulationResponse)
async def simulate(request: SimulationRequest):
    result = engine.run_simulation(request.dict())
    return result

@app.get("/api/health")
async def health_check():
    return {"status": "active", "system": "PolyBio Markov Engine"}