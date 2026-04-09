import pandas as pd
import os

# 1. Path Management
# Points to the 'python_scripts' folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Points to the 'bike-store-project' root
BASE_DIR = os.path.dirname(SCRIPT_DIR)

# 2. Check both the Root and the Data folder for the CSV
possible_paths = [
    os.path.join(BASE_DIR, 'sales_summary.csv'),        # Option A: Root
    os.path.join(BASE_DIR, 'data', 'sales_summary.csv') # Option B: Data Folder
]

CSV_PATH = None
for path in possible_paths:
    if os.path.exists(path):
        CSV_PATH = path
        break

# 3. Execution Logic
if not CSV_PATH:
    print("❌ Error: 'sales_summary.csv' not found!")
    print(f"Searched in: {BASE_DIR} and {os.path.join(BASE_DIR, 'data')}")
    print("Make sure you ran 'python_scripts/data_loader.py' first.")
else:
    print(f"✅ Found data at: {CSV_PATH}")
    
    try:
        # Loading the data
        df = pd.read_csv(CSV_PATH, parse_dates=['order_date'])
        
        print("\n" + "="*30)
        print("🚀 DATA PREVIEW")
        print("="*30)
        print(df.head())
        
        print("\n" + "="*30)
        print("📊 DATASET INFO")
        print("="*30)
        df.info()
        
    except Exception as e:
        print(f"❌ An error occurred while reading the CSV: {e}")