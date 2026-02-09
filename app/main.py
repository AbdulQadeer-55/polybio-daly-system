from fastapi import FastAPI, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import SimulationRequest, SimulationResponse
from app.engine import PolyBioEngine
from app.reporting import ReportGenerator

app = FastAPI(title="PolyBio DALY Model API", version="2.1")

# CORS: fine for iframe embeds; tighten later if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = PolyBioEngine()

# Static frontend
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
async def read_root():
    return FileResponse("static/index.html")


@app.post("/api/simulate", response_model=SimulationResponse)
async def simulate(request: SimulationRequest):
    payload = request.model_dump()  # pydantic v2 (use .dict() if on v1)
    # If you're on pydantic v1, replace with: payload = request.dict()

    # Simulation should ignore charts even if present
    payload.pop("charts", None)
    return engine.run_simulation(payload)


@app.post("/api/export/csv")
async def export_csv(request: SimulationRequest):
    payload = request.model_dump()
    payload.pop("charts", None)

    data = engine.run_simulation(payload)
    csv_file = ReportGenerator.generate_csv(data)

    return Response(
        content=csv_file.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=PolyBio_Results.csv"},
    )


@app.post("/api/export/pdf")
async def export_pdf(request: SimulationRequest):
    payload = request.model_dump()

    # Run sim without charts
    sim_payload = dict(payload)
    sim_payload.pop("charts", None)

    data = engine.run_simulation(sim_payload)

    try:
        # Pass full payload including charts to PDF generator
        pdf_bytes = ReportGenerator.generate_pdf(data, payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=PolyBio_Report.pdf"},
    )
