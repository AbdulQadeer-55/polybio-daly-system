from pydantic import BaseModel, Field
from typing import Dict, Optional


class ChartsPayload(BaseModel):
    """
    Base64 data URLs from the frontend (Chart.js canvas.toDataURL("image/png"))
    Example: "data:image/png;base64,iVBORw0KGgoAAA..."
    """
    daly: Optional[str] = Field(default=None, description="Baseline vs Scenario stacked bar chart")
    pasc: Optional[str] = Field(default=None, description="PASC composition doughnut chart")
    mort: Optional[str] = Field(default=None, description="Death vs Disability pie chart")
    age: Optional[str] = Field(default=None, description="Age cohorts bar chart")


class SimulationRequest(BaseModel):
    clean_air: bool = False
    diagnostics: bool = False
    nose_sprays: bool = False
    acute_treatment: bool = False
    lc_treatment: bool = False

    # ✅ New: charts can be sent ONLY for /api/export/pdf (safe to ignore in simulate)
    charts: Optional[ChartsPayload] = None


class DALYBreakdown(BaseModel):
    acute: int
    long_covid: int
    pasc: int
    yll: int
    yld: int


class AgeBreakdown(BaseModel):
    group_0_17: int
    group_18_64: int
    group_65_plus: int


class SimulationResponse(BaseModel):
    baseline_dalys: int
    simulated_dalys: int
    dalys_averted: int
    reduction_percentage: float
    breakdown: DALYBreakdown
    age_breakdown: AgeBreakdown
    pasc_condition_breakdown: Dict[str, int]
