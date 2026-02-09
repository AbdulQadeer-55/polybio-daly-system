import json
import os
from typing import Dict, Any


class PolyBioEngine:
    def __init__(self):
        self.constants_path = "data/processed/model_constants.json"
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.constants_path):
            with open(self.constants_path, "r") as f:
                data = json.load(f)

            # Ensure these exist even if constants json is minimal
            data.setdefault("breakdown_shares", {})
            data["breakdown_shares"].setdefault("yll_share", 0.855)
            data["breakdown_shares"].setdefault("yld_share", 0.145)

            data.setdefault("pasc_weights", {
                "Cardiovascular": 0.41, "Diabetes": 0.16, "Neurological": 0.12,
                "Kidney": 0.09, "Gastrointestinal": 0.08, "Musculoskeletal": 0.08, "Other": 0.06
            })
            return data

        # fallback defaults
        return {
            "baseline_dalys": 362095599,
            "breakdown_shares": {
                "acute_share": 0.1766,
                "long_covid_share": 0.0112,
                "pasc_share": 0.8122,
                "yll_share": 0.855,
                "yld_share": 0.145
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
                "Cardiovascular": 0.41, "Diabetes": 0.16, "Neurological": 0.12,
                "Kidney": 0.09, "Gastrointestinal": 0.08, "Musculoskeletal": 0.08, "Other": 0.06
            }
        }

    def run_simulation(self, request_dict: Dict[str, Any]) -> Dict[str, Any]:
        # Ignore charts payload if present
        request_dict = dict(request_dict)
        request_dict.pop("charts", None)

        eff = self.data["efficacies"]
        base_dalys = float(self.data["baseline_dalys"])
        shares = self.data["breakdown_shares"]

        # --- Multiplicative modifiers (keep full float precision) ---
        mod_infection = 1.0
        if request_dict.get("clean_air"):     mod_infection *= (1.0 - float(eff["clean_air"]))
        if request_dict.get("nose_sprays"):   mod_infection *= (1.0 - float(eff["nose_sprays"]))
        if request_dict.get("diagnostics"):   mod_infection *= (1.0 - float(eff["diagnostics_risk"]))

        mod_severity = 1.0
        if request_dict.get("diagnostics"):       mod_severity *= (1.0 - float(eff["diagnostics_sev"]))
        if request_dict.get("acute_treatment"):   mod_severity *= (1.0 - float(eff["acute_tx_sev"]))

        mod_pasc_incidence = 1.0
        if request_dict.get("acute_treatment"):
            mod_pasc_incidence *= (1.0 - float(eff["acute_tx_pasc"]))

        mod_lc_severity = 1.0
        if request_dict.get("lc_treatment"):
            mod_lc_severity *= (1.0 - float(eff["lc_tx_severity"]))

        # --- Component DALYs (float) ---
        sim_acute_f = (base_dalys * float(shares["acute_share"])) * mod_infection * mod_severity
        sim_lc_f    = (base_dalys * float(shares["long_covid_share"])) * mod_infection * mod_lc_severity
        sim_pasc_f  = (base_dalys * float(shares["pasc_share"])) * mod_infection * mod_pasc_incidence

        total_sim_f = sim_acute_f + sim_lc_f + sim_pasc_f
        dalys_av_f  = base_dalys - total_sim_f

        # ✅ Use ROUND not truncation to match hand-math / spreadsheet expectations
        total_simulated = int(round(total_sim_f))
        dalys_averted = int(round(dalys_av_f))

        reduction_pct = 0.0
        if base_dalys > 0:
            reduction_pct = round((dalys_averted / base_dalys) * 100.0, 1)

        yll_share = float(shares.get("yll_share", 0.855))
        yld_share = float(shares.get("yld_share", 0.145))

        yll_val = int(round(total_simulated * yll_share))
        yld_val = int(round(total_simulated * yld_share))

        # If you later replace these with real excel-derived age shares, it's isolated here
        age_breakdown = {
            "group_0_17": int(round(total_simulated * 0.041)),
            "group_18_64": int(round(total_simulated * 0.497)),
            "group_65_plus": int(round(total_simulated * 0.462)),
        }

        pasc_weights = self.data.get("pasc_weights", {})
        # Use float sim_pasc_f to avoid rounding drift, then round
        pasc_condition_breakdown = {
            k: int(round(sim_pasc_f * float(v))) for k, v in pasc_weights.items()
        }

        return {
            "baseline_dalys": int(round(base_dalys)),
            "simulated_dalys": total_simulated,
            "dalys_averted": dalys_averted,
            "reduction_percentage": reduction_pct,
            "breakdown": {
                "acute": int(round(sim_acute_f)),
                "long_covid": int(round(sim_lc_f)),
                "pasc": int(round(sim_pasc_f)),
                "yll": yll_val,
                "yld": yld_val,
            },
            "age_breakdown": age_breakdown,
            "pasc_condition_breakdown": pasc_condition_breakdown,
        }
