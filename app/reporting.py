from fpdf import FPDF
import csv
import io
from datetime import datetime
import base64
import tempfile
import os
from typing import Dict, Any, Optional


class ReportGenerator:
    @staticmethod
    def generate_csv(data: dict):
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["PolyBio Research Foundation | DALY Simulation Report"])
        writer.writerow(["Generated On", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow([])

        writer.writerow(["METRIC", "VALUE"])
        writer.writerow(["Baseline DALYs", f"{data['baseline_dalys']:,}"])
        writer.writerow(["Simulated DALYs", f"{data['simulated_dalys']:,}"])
        writer.writerow(["DALYs Averted", f"{data['dalys_averted']:,}"])
        writer.writerow(["Reduction %", f"{data['reduction_percentage']}%"])
        writer.writerow([])

        writer.writerow(["CATEGORY", "DALYs"])
        writer.writerow(["Acute COVID", f"{data['breakdown']['acute']:,}"])
        writer.writerow(["Long COVID", f"{data['breakdown']['long_covid']:,}"])
        writer.writerow(["PASC (Organ Disease)", f"{data['breakdown']['pasc']:,}"])
        writer.writerow(["YLL (Deaths)", f"{data['breakdown']['yll']:,}"])
        writer.writerow(["YLD (Disability)", f"{data['breakdown']['yld']:,}"])

        output.seek(0)
        return output

    # ---------- Helpers ----------
    @staticmethod
    def _pretty_intervention_name(key: str) -> str:
        mapping = {
            "clean_air": "Clean Indoor Air",
            "diagnostics": "Rapid Diagnostics",
            "nose_sprays": "Nose Sprays",
            "acute_treatment": "Acute Treatment",
            "lc_treatment": "Long COVID Treatment",
        }
        return mapping.get(key, key.replace("_", " ").title())

    @staticmethod
    def _data_url_to_temp_png(data_url: str) -> Optional[str]:
        """
        Accepts: "data:image/png;base64,...."
        Returns: temp png filepath or None
        """
        if not data_url or not isinstance(data_url, str):
            return None
        if "base64," not in data_url:
            return None
        try:
            b64 = data_url.split("base64,", 1)[1]
            raw = base64.b64decode(b64)
            fd, path = tempfile.mkstemp(suffix=".png")
            with os.fdopen(fd, "wb") as f:
                f.write(raw)
            return path
        except Exception:
            return None

    @staticmethod
    def _section_title(pdf: FPDF, text: str):
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, text, ln=True)
        pdf.ln(1)

    @staticmethod
    def _add_kv_table(pdf: FPDF, rows):
        def add_row(label, val, bold=False):
            pdf.set_font("Arial", "B" if bold else "", 11)
            pdf.cell(110, 8, label, border=1)
            pdf.cell(70, 8, val, border=1, ln=True)

        for r in rows:
            add_row(r["label"], r["value"], r.get("bold", False))

    @staticmethod
    def _add_chart_grid(pdf: FPDF, chart_paths: Dict[str, str]):
        """
        2 charts per row, auto page breaks
        """
        # sizing (A4 width ~ 210mm; margins default 10)
        left_x = 10
        col_w = 90
        gap = 10
        img_h = 55

        items = [
            ("Total Impact (Baseline vs Scenario)", chart_paths.get("daly")),
            ("PASC Composition", chart_paths.get("pasc")),
            ("Death vs Disability (YLL vs YLD)", chart_paths.get("mort")),
            ("Age Cohorts", chart_paths.get("age")),
        ]

        # Filter missing
        items = [(t, p) for (t, p) in items if p]

        if not items:
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(120, 120, 120)
            pdf.multi_cell(0, 6, "No chart images were provided in the request payload.")
            return

        pdf.ln(2)
        ReportGenerator._section_title(pdf, "Charts")

        for idx, (title, path) in enumerate(items):
            # page break if needed
            if pdf.get_y() + img_h + 18 > 280:
                pdf.add_page()

            col = idx % 2
            row_x = left_x + (col * (col_w + gap))
            y = pdf.get_y()

            pdf.set_xy(row_x, y)
            pdf.set_font("Arial", "B", 10)
            pdf.multi_cell(col_w, 5, title)

            # move below title
            y_img = pdf.get_y()
            pdf.image(path, x=row_x, y=y_img, w=col_w, h=img_h)

            # after placing 2nd column, move cursor down to next row
            if col == 1:
                pdf.set_y(y_img + img_h + 10)
            else:
                # keep y for second column aligned
                pdf.set_y(y)

        # if odd number of charts, move cursor below the last image
        if len(items) % 2 == 1:
            pdf.set_y(pdf.get_y() + img_h + 10)

    # ---------- PDF ----------
    @staticmethod
    def generate_pdf(data: dict, request_dict: dict):
        """
        request_dict can include request_dict["charts"] = {daly,pasc,mort,age} as base64 data URLs
        """
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=12)
        pdf.add_page()

        # Header
        pdf.set_text_color(35, 52, 171)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "PolyBio Research Foundation | DALY Simulation Report", ln=True, align="C")

        pdf.set_text_color(100, 100, 100)
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
        pdf.ln(6)

        # Active interventions (ignore charts key)
        ReportGenerator._section_title(pdf, "Active Interventions")
        pdf.set_font("Arial", "", 11)

        active = []
        for k, v in request_dict.items():
            if k == "charts":
                continue
            if isinstance(v, bool) and v:
                active.append(ReportGenerator._pretty_intervention_name(k))

        if not active:
            pdf.cell(0, 7, "- Status Quo (No Interventions)", ln=True)
        else:
            for item in active:
                pdf.cell(0, 7, f"- {item}", ln=True)

        pdf.ln(4)

        # Summary
        ReportGenerator._section_title(pdf, "Projected Impact (DALYs)")
        rows = [
            {"label": "Baseline DALYs", "value": f"{data['baseline_dalys']:,}"},
            {"label": "Total DALYs (Scenario)", "value": f"{data['simulated_dalys']:,}", "bold": True},
            {"label": "DALYs Averted", "value": f"{data['dalys_averted']:,}", "bold": True},
            {"label": "Reduction %", "value": f"{data['reduction_percentage']}%"},
        ]
        ReportGenerator._add_kv_table(pdf, rows)

        pdf.ln(5)

        # Breakdown
        ReportGenerator._section_title(pdf, "Detailed Breakdown")
        rows2 = [
            {"label": "Acute COVID", "value": f"{data['breakdown']['acute']:,}"},
            {"label": "Long COVID", "value": f"{data['breakdown']['long_covid']:,}"},
            {"label": "PASC (Organ Disease)", "value": f"{data['breakdown']['pasc']:,}"},
            {"label": "YLL (Premature Death)", "value": f"{data['breakdown']['yll']:,}"},
            {"label": "YLD (Disability)", "value": f"{data['breakdown']['yld']:,}"},
        ]
        ReportGenerator._add_kv_table(pdf, rows2)

        # Charts
        chart_paths: Dict[str, str] = {}
        temp_files = []

        charts = request_dict.get("charts") or {}
        if isinstance(charts, dict):
            for key in ["daly", "pasc", "mort", "age"]:
                p = ReportGenerator._data_url_to_temp_png(charts.get(key))
                if p:
                    chart_paths[key] = p
                    temp_files.append(p)

        try:
            ReportGenerator._add_chart_grid(pdf, chart_paths)
            return pdf.output(dest="S").encode("latin-1")  # type: ignore
        finally:
            # cleanup temp pngs
            for p in temp_files:
                try:
                    os.remove(p)
                except Exception:
                    pass
