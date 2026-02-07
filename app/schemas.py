from pydantic import BaseModel

class SimulationRequest(BaseModel):
    """
    State of the 5 toggles from the frontend.
    True = Intervention Enabled.
    """
    clean_air: bool
    diagnostics: bool
    nose_sprays: bool
    acute_treatment: bool
    lc_treatment: bool

class DALYBreakdown(BaseModel):
    """
    Breakdown of the DALY burden by disease stage.
    """
    acute: int
    long_covid: int
    pasc: int

class AgeBreakdown(BaseModel):
    """
    Breakdown of the total DALY burden by age cohort.
    """
    group_0_17: int
    group_18_64: int
    group_65_plus: int

class SimulationResponse(BaseModel):
    """
    The full results object sent back to the UI.
    """
    baseline_dalys: int
    simulated_dalys: int
    dalys_averted: int
    reduction_percentage: float
    breakdown: DALYBreakdown
    age_breakdown: AgeBreakdown