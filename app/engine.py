import json
import os
# Absolute imports to fix ModuleNotFoundError
from app.schemas import SimulationRequest, SimulationResponse, DALYBreakdown, AgeBreakdown

class PolyBioEngine:
    def __init__(self):
        # Path to the JSON constants
        self.constants_path = "data/processed/model_constants.json"
        self.data = self._load_data()

    def _load_data(self):
        """
        Loads scientific constants. Uses robust defaults if JSON is missing.
        """
        if os.path.exists(self.constants_path):
            with open(self.constants_path, "r") as f:
                return json.load(f)
        else:
            print("⚠️ Warning: JSON not found. Using hardcoded scientific defaults.")
            return {
                "baseline_dalys": 362095599,
                "breakdown_shares": {
                    "acute_share": 0.1766,
                    "long_covid_share": 0.0112,
                    "pasc_share": 0.8122
                },
                "efficacies": {
                    "clean_air": 0.74,
                    "nose_sprays": 0.57,
                    "diagnostics_risk": 0.20,
                    "diagnostics_sev": 0.25,
                    "acute_tx_sev": 0.64,
                    "acute_tx_pasc": 0.26,
                    "lc_tx_severity": 0.55
                }
            }

    def run_simulation(self, request_dict: dict) -> dict:
        """
        Calculates DALY reduction using Multiplicative Factors.
        """
        eff = self.data["efficacies"]
        base_dalys = self.data["baseline_dalys"]
        shares = self.data["breakdown_shares"]

        # --- 1. CALCULATE MODIFIERS ---
        # Multiplicative Logic: New Risk = Old Risk * (1 - Efficacy)
        
        # A. Infection Risk Modifier (Clean Air, Nose Sprays, Diagnostics)
        mod_infection = 1.0
        if request_dict["clean_air"]:
            mod_infection *= (1.0 - eff["clean_air"])
        if request_dict["nose_sprays"]:
            mod_infection *= (1.0 - eff["nose_sprays"])
        if request_dict["diagnostics"]:
            mod_infection *= (1.0 - eff["diagnostics_risk"])

        # B. Severity Modifier (Diagnostics, Acute Treatment)
        mod_severity = 1.0
        if request_dict["diagnostics"]:
            mod_severity *= (1.0 - eff["diagnostics_sev"])
        if request_dict["acute_treatment"]:
            mod_severity *= (1.0 - eff["acute_tx_sev"])

        # C. PASC Incidence Modifier (Acute Treatment)
        mod_pasc_incidence = 1.0
        if request_dict["acute_treatment"]:
            mod_pasc_incidence *= (1.0 - eff["acute_tx_pasc"])

        # D. Long COVID Severity Modifier (LC Treatment)
        mod_lc_severity = 1.0
        if request_dict["lc_treatment"]:
            mod_lc_severity *= (1.0 - eff["lc_tx_severity"])

        # --- 2. APPLY TO BUCKETS ---
        
        # Bucket 1: Acute DALYs (Depends on Infection & Severity)
        base_acute = base_dalys * shares["acute_share"]
        sim_acute = base_acute * mod_infection * mod_severity

        # Bucket 2: Long COVID DALYs (Depends on Infection & LC Severity)
        base_lc = base_dalys * shares["long_covid_share"]
        sim_lc = base_lc * mod_infection * mod_lc_severity

        # Bucket 3: PASC DALYs (Depends on Infection & PASC Incidence)
        base_pasc = base_dalys * shares["pasc_share"]
        sim_pasc = base_pasc * mod_infection * mod_pasc_incidence

        # --- 3. AGGREGATE RESULTS ---
        total_simulated = int(sim_acute + sim_lc + sim_pasc)
        dalys_averted = int(base_dalys - total_simulated)
        
        reduction_pct = 0.0
        if base_dalys > 0:
            reduction_pct = round((dalys_averted / base_dalys) * 100, 1)

        # Estimate Age Breakdown (Fixed proportions from demographics)
        age_breakdown = {
            "group_0_17": int(total_simulated * 0.041),
            "group_18_64": int(total_simulated * 0.497),
            "group_65_plus": int(total_simulated * 0.462)
        }

        return {
            "baseline_dalys": base_dalys,
            "simulated_dalys": total_simulated,
            "dalys_averted": dalys_averted,
            "reduction_percentage": reduction_pct,
            "breakdown": {
                "acute": int(sim_acute),
                "long_covid": int(sim_lc),
                "pasc": int(sim_pasc)
            },
            "age_breakdown": age_breakdown
        }