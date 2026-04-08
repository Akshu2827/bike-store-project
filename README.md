# 🚴 Bike Store Data Project

## 📌 Overview
This project builds an end-to-end data pipeline for analyzing bike store sales data — from raw CSV ingestion to database storage, processing, and visualization.

---

## ⚙️ Workflow

1. **Data Source**
   - Raw CSV files stored in `/data`

2. **Database Initialization**
   - `sql_scripts/init_db.sql`
   - Creates tables and loads initial data into the database

3. **Data Processing**
   - `python_scripts/data_loader.py`
   - Extracts data from MySQL/PostgreSQL and exports cleaned datasets

4. **Model / Analysis (Future Scope)**
   - `python_scripts/model_pipeline.py`
   - Placeholder for ML models and advanced analytics

5. **Visualization**
   - `power_bi/sales_analysis.pbix`
   - Interactive dashboard for business insights

---

## 📂 Project Structure