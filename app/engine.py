import json
import os
from app.schemas import SimulationRequest, SimulationResponse

class PolyBioEngine:
    def __init__(self):
        self.constants_path = "data/processed/model_constants.json"
        self.data = self._load_data()

    def _load_data(self):
        if os.path.exists(self.constants_path):
            with open(self.constants_path, "r") as f:
                return json.load(f)
        else:
            # Fallback Defaults
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
                },
                "pasc_weights": {
                    "Cardiovascular": 0.41,
                    "Diabetes": 0.16,
                    "Neurological": 0.12,
                    "Kidney": 0.09,
                    "Gastrointestinal": 0.08,
                    "Musculoskeletal": 0.08,
                    "Other": 0.06
                }
            }

    def run_simulation(self, request_dict: dict) -> dict:
        eff = self.data["efficacies"]
        base_dalys = self.data["baseline_dalys"]
        shares = self.data["breakdown_shares"]

        # --- 1. CALCULATE MODIFIERS ---
        mod_infection = 1.0
        if request_dict["clean_air"]: mod_infection *= (1.0 - eff["clean_air"])
        if request_dict["nose_sprays"]: mod_infection *= (1.0 - eff["nose_sprays"])
        if request_dict["diagnostics"]: mod_infection *= (1.0 - eff["diagnostics_risk"])

        mod_severity = 1.0
        if request_dict["diagnostics"]: mod_severity *= (1.0 - eff["diagnostics_sev"])
        if request_dict["acute_treatment"]: mod_severity *= (1.0 - eff["acute_tx_sev"])

        mod_pasc_incidence = 1.0
        if request_dict["acute_treatment"]: mod_pasc_incidence *= (1.0 - eff["acute_tx_pasc"])

        mod_lc_severity = 1.0
        if request_dict["lc_treatment"]: mod_lc_severity *= (1.0 - eff["lc_tx_severity"])

        # --- 2. APPLY TO BUCKETS ---
        sim_acute = (base_dalys * shares["acute_share"]) * mod_infection * mod_severity
        sim_lc = (base_dalys * shares["long_covid_share"]) * mod_infection * mod_lc_severity
        sim_pasc = (base_dalys * shares["pasc_share"]) * mod_infection * mod_pasc_incidence

        # --- 3. AGGREGATE ---
        total_simulated = int(sim_acute + sim_lc + sim_pasc)
        dalys_averted = int(base_dalys - total_simulated)
        
        reduction_pct = 0.0
        if base_dalys > 0:
            reduction_pct = round((dalys_averted / base_dalys) * 100, 1)

        # --- 4. BREAKDOWNS ---
        age_breakdown = {
            "group_0_17": int(total_simulated * 0.041),
            "group_18_64": int(total_simulated * 0.497),
            "group_65_plus": int(total_simulated * 0.462)
        }

        pasc_weights = self.data.get("pasc_weights", {
            "Cardiovascular": 0.41, "Diabetes": 0.16, "Neurological": 0.12, 
            "Kidney": 0.09, "Gastrointestinal": 0.08, "Musculoskeletal": 0.08, "Other": 0.06
        })
        
        pasc_condition_breakdown = {
            k: int(sim_pasc * v) for k, v in pasc_weights.items()
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
            "age_breakdown": age_breakdown,
            "pasc_condition_breakdown": pasc_condition_breakdown
        }