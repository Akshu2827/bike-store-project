import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
import logging

pd.set_option('display.max_columns', None)
load_dotenv()
password = quote_plus(os.getenv('DB_PASSWORD'))

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{password}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# Always save next to this script's parent folder (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'sales_summary.csv')

def load_data():
    print("🚀 Bike Store Data Loader Started (PostgreSQL)...")
    try:
        with engine.connect() as conn:
            print("✅ Successfully connected to PostgreSQL!")

        df = pd.read_sql("SELECT * FROM sales_summary", engine)
        print(f"✅ Successfully loaded {len(df):,} rows from sales_summary")
        print(df.tail())
        print(f"shape: {df.shape}")

        assert df['quantity'].min() >= 0
        assert df['list_price'].min() > 0
        assert df['discount'].between(0, 1).all()

        # Save to explicit path
        df.to_csv(CSV_PATH, index=False)
        print(f"💾 Exported to: {CSV_PATH}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    load_data()