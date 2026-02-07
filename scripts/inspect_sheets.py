import pandas as pd
import os

FILE_PATH = "data/raw/PolyBio Long COVID Economic Model_Final.xlsm"

def inspect():
    if not os.path.exists(FILE_PATH):
        print(f"ERROR: File not found at {FILE_PATH}")
        return

    print(f"--- INSPECTING EXCEL STRUCTURE ---")
    try:
        xls = pd.ExcelFile(FILE_PATH)
        
        print(f"\n[SHEET NAMES FOUND]")
        for i, sheet in enumerate(xls.sheet_names):
            print(f"{i}: {sheet}")
            
        print(f"\n[PREVIEW OF FIRST SHEET: {xls.sheet_names[0]}]")
        df = pd.read_excel(xls, sheet_name=0, header=None, nrows=5)
        print(df.to_string())
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    inspect()