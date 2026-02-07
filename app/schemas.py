from pydantic import BaseModel
from typing import Dict

class SimulationRequest(BaseModel):
    clean_air: bool
    diagnostics: bool
    nose_sprays: bool
    acute_treatment: bool
    lc_treatment: bool

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