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

# Data Analytics / ML Problem Statements


# Question 1 — "How much revenue will we make next month?"

**Model:** Time Series Forecasting (Revenue Prediction)

**Features to use:**
- order_date
- revenue
- store_name
- category_name

**Business value:**
- Inventory planning
- staff scheduling
- sales targets.

---

# Question 2 — "Which customers are about to stop buying?"

**Model:** Customer Churn Classification

**Features to use:**
- total orders per customer
- avg revenue
- avg discount
- days since last order
- favourite category

**Business value:**
- Trigger retention campaigns for at-risk customers.

---

**Question 3 "Which products should we stock more of, and which should we drop?"**

**Model: Product Portfolio Optimization**
- category_name + brand_name + quantity + revenue → 
- identify high revenue / low stock risk products
- identify low revenue / high discount products (dead weight)

Controllable action: Reorder bestsellers earlier, discontinue dead stock, negotiate better with top brands.
What makes it controllable: Purchasing and inventory decisions are fully internal.

