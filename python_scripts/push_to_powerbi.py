import pandas as pd
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = r'E:\Mostly_everything_related_to_coding_DS\business_case_studies\bike-store-project\bike-store-project'
CSV_PATH = os.path.join(BASE_DIR, 'sales_summary.csv')

# Power BI REST API credentials (from Azure App Registration)
TENANT_ID    = os.getenv('PBI_TENANT_ID')
CLIENT_ID    = os.getenv('PBI_CLIENT_ID')
CLIENT_SECRET= os.getenv('PBI_CLIENT_SECRET')
WORKSPACE_ID = os.getenv('PBI_WORKSPACE_ID')
DATASET_ID   = os.getenv('PBI_DATASET_ID')

def get_access_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'https://analysis.windows.net/powerbi/api/.default'
    }
    r = requests.post(url, data=payload)
    return r.json()['access_token']

def push_rows(token, df):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/datasets/{DATASET_ID}/tables/sales_summary/rows"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    # Push in chunks of 1000 (API limit)
    chunk_size = 1000
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size]
        payload = {"rows": chunk.to_dict(orient='records')}
        r = requests.post(url, headers=headers, json=payload)
        print(f"✅ Pushed rows {i}–{i+len(chunk)}: {r.status_code}")

if __name__ == "__main__":
    df = pd.read_csv(CSV_PATH, parse_dates=['order_date'])
    df['order_date'] = df['order_date'].astype(str)  # API needs string dates
    token = get_access_token()
    push_rows(token, df)
    print("🎉 Data pushed to Power BI!")