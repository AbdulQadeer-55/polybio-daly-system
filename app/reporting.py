from fpdf import FPDF
import csv
import io
from datetime import datetime

class ReportGenerator:
    @staticmethod
    def generate_csv(data: dict):
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(["PolyBio DALY Simulation Report"])
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

    @staticmethod
    def generate_pdf(data: dict, request_dict: dict):
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_text_color(35, 52, 171) 
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "PolyBio Research | DALY Simulation Report", ln=True, align="C")
        
        pdf.set_text_color(100, 100, 100)
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
        pdf.ln(10)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Active Interventions:", ln=True)
        pdf.set_font("Arial", "", 11)
        
        active = [k.replace('_', ' ').title() for k, v in request_dict.items() if v]
        if not active:
            pdf.cell(0, 8, "- Status Quo (No Interventions)", ln=True)
        else:
            for item in active:
                pdf.cell(0, 8, f"- {item}", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Projected Impact:", ln=True)
        
        def add_row(label, val, bold=False):
            pdf.set_font("Arial", "B" if bold else "", 11)
            pdf.cell(100, 8, label, border=1)
            pdf.cell(50, 8, f"{val:,}", border=1, ln=True)

        add_row("Total DALYs (Scenario)", data['simulated_dalys'], True)
        add_row("DALYs Averted", data['dalys_averted'], True)
        
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Detailed Breakdown:", ln=True)
        add_row("Acute COVID", data['breakdown']['acute'])
        add_row("PASC (Organ Disease)", data['breakdown']['pasc'])
        add_row("YLL (Premature Death)", data['breakdown']['yll'])
        add_row("YLD (Disability)", data['breakdown']['yld'])

        return pdf.output(dest='S').encode('latin-1') # type: ignore