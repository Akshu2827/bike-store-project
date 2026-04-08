import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus

pd.set_option('display.max_columns', None)

# Load variables from .env file
load_dotenv()
password = quote_plus(os.getenv('DB_PASSWORD'))

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{password}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

def load_data():
    print("🚀 Bike Store Data Loader Started (PostgreSQL)...")

    try:
        # Test the connection
        with engine.connect() as conn:
            print("✅ Successfully connected to PostgreSQL!")

        # Load the main view
        df = pd.read_sql("SELECT * FROM sales_summary ORDER BY order_date DESC LIMIT 1000", engine)
        
        print(f"✅ Successfully loaded {len(df):,} rows from sales_summary")

        # Show sample data
        print("\nSample Data:")
        print(df.tail())

        # Export for Power BI
        df.to_csv('sales_summary.csv', index=False)
        print("💾 Exported sales_summary.csv successfully!")

        print("\n🎉 All done! You can now open sales_summary.csv in Power BI.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    load_data()