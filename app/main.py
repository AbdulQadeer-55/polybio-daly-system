from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import SimulationRequest, SimulationResponse
from app.engine import PolyBioEngine
from app.reporting import ReportGenerator

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
    return engine.run_simulation(request.dict())

@app.post("/api/export/csv")
async def export_csv(request: SimulationRequest):
    data = engine.run_simulation(request.dict())
    csv_file = ReportGenerator.generate_csv(data)
    return Response(
        content=csv_file.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=PolyBio_Results.csv"}
    )

@app.post("/api/export/pdf")
async def export_pdf(request: SimulationRequest):
    data = engine.run_simulation(request.dict())
    pdf_bytes = ReportGenerator.generate_pdf(data, request.dict())
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=PolyBio_Report.pdf"}
    )