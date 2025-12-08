#!/usr/bin/env python3
"""Quick script to check shelter data format."""

import sys
sys.path.insert(0, '/home/user/emergency')

try:
    import pandas as pd

    # Load the shelter data
    df = pd.read_excel('shelters_downloaded.xlsx')

    print("="*60)
    print("SHELTER DATA CHECK")
    print("="*60)
    print(f"Total rows: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    print("\n" + "="*60)
    print("FIRST ROW:")
    print("="*60)
    for col in df.columns:
        print(f"{col}: {df.iloc[0][col]} (type: {type(df.iloc[0][col]).__name__})")

    print("\n" + "="*60)
    print("DATA TYPES:")
    print("="*60)
    print(df.dtypes)

    print("\n" + "="*60)
    print("SAMPLE DATA (first 3 rows):")
    print("="*60)
    print(df.head(3).to_string())

except ImportError as e:
    print(f"Error importing pandas: {e}")
    print("Trying to install pandas...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pandas", "openpyxl"])
    print("\nPlease run this script again after pandas is installed.")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
