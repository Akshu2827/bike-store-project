import pandas as pd
import numpy as np
import os
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import (
    StandardScaler, OneHotEncoder, OrdinalEncoder
)
from sklearn.model_selection import TimeSeriesSplit
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, mean_absolute_error, r2_score
)
import warnings
warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None)

#point to which python script folder is
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
OUT_DIR   = os.path.join(BASE_DIR, 'outputs')
path = os.path.join(BASE_DIR, 'sales_summary.csv')
df = pd.read_csv(path, parse_dates=['order_date'])

print(df.head())
print(f'data information: {df.info()}')

# Convert to datetime (FIX)
df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')

# Sort by time (VERY IMPORTANT for time series)
df = df.sort_values(by='order_date')

# ─────────────────────────────────────────────
# SHARED DATE FEATURES (used across all models)
# ─────────────────────────────────────────────
df['month'] = df['order_date'].dt.month
df['quarter'] = df['order_date'].dt.quarter
df['day_of_week'] = df['order_date'].dt.dayofweek
df['year'] = df['order_date'].dt.year

# ══════════════════════════════════════════════
# QUESTION 2 — REVENUE FORECASTING
# ══════════════════════════════════════════════
print("=" * 50)
print("Q2: Revenue Forecasting")
print("=" * 50)

# Feature engineering
q2 = df.copy()

# Numerical → StandardScaler
q2_numerical = ['quantity', 'discount', 'list_price',
                 'month', 'quarter', 'day_of_week', 'year']

# Nominal → OneHotEncoder
q2_nominal   = ['store_name', 'category_name', 'state']

# Ordinal → OrdinalEncoder
q2_ordinal   = ['order_status']
order_status_categories = [[1, 2, 3, 4]]

q2_preprocessor = ColumnTransformer(transformers=[
    ('num',     StandardScaler(), q2_numerical),
    ('nom',     OneHotEncoder(handle_unknown='ignore', sparse_output=False), q2_nominal),
    ('ord',     OrdinalEncoder(categories=order_status_categories), q2_ordinal),
], remainder='drop')

X_q2 = q2[q2_numerical + q2_nominal + q2_ordinal]
y_q2 = q2['revenue']

# Time Series Cross Validation
tscv = TimeSeriesSplit(n_splits=5)

mae_scores = []
r2_scores = []

q2_pipeline = Pipeline([
    ('preprocessor', q2_preprocessor),
    ('model',        RandomForestRegressor(n_estimators=100, random_state=42))
])

for train_index, test_index in tscv.split(X_q2):
    X_train, X_test = X_q2.iloc[train_index], X_q2.iloc[test_index]
    y_train, y_test = y_q2.iloc[train_index], y_q2.iloc[test_index]

    q2_pipeline.fit(X_train, y_train)
    y_pred_q2 = q2_pipeline.predict(X_test)

    mae_scores.append(mean_absolute_error(y_test, y_pred_q2))
    r2_scores.append(r2_score(y_test, y_pred_q2))

print(f"Average MAE : ${sum(mae_scores)/len(mae_scores):,.2f}")
print(f"Average R²  : {sum(r2_scores)/len(r2_scores):.4f}")

# Save predictions
q2_results = X_test.copy()
q2_results['actual_revenue']    = y_test.values
q2_results['predicted_revenue'] = y_pred_q2

q2_results.to_csv('q2_revenue_forecast.csv')
print("✅ Saved q2_revenue_forecast.csv\n")


# ══════════════════════════════════════════════
# QUESTION 3 — CUSTOMER CHURN
# ══════════════════════════════════════════════
print("=" * 50)
print("Q3: Customer Churn Prediction")
print("=" * 50)

# Aggregate to customer level — one row per customer
snapshot_date = df['order_date'].max()

q3 = df.groupby('customer_name').agg(
    total_orders      = ('order_id',    'nunique'),      # numerical
    total_revenue     = ('revenue',     'sum'),          # numerical
    avg_revenue       = ('revenue',     'mean'),         # numerical
    avg_discount      = ('discount',    'mean'),         # numerical
    avg_quantity      = ('quantity',    'mean'),         # numerical
    days_since_order  = ('order_date',
                         lambda x: (snapshot_date - x.max()).days),  # numerical
    favourite_category= ('category_name', lambda x: x.mode()[0]),    # nominal
    favourite_state   = ('state',         lambda x: x.mode()[0]),    # nominal
).reset_index()

# Target: churned if no order in last 365 days
q3['churned'] = (q3['days_since_order'] > 365).astype(int)
print(f"Churn rate: {q3['churned'].mean():.1%}")

# Numerical → StandardScaler
q3_numerical = ['total_orders', 'total_revenue', 'avg_revenue',
                 'avg_discount', 'avg_quantity', 'days_since_order']

# Nominal → OneHotEncoder
q3_nominal   = ['favourite_category', 'favourite_state']

q3_preprocessor = ColumnTransformer(transformers=[
    ('num', StandardScaler(),
            q3_numerical),
    ('nom', OneHotEncoder(handle_unknown='ignore', sparse_output=False),
            q3_nominal),
], remainder='drop')

X_q3 = q3[q3_numerical + q3_nominal]
y_q3 = q3['churned']

X_train, X_test, y_train, y_test = train_test_split(
    X_q3, y_q3, test_size=0.2, random_state=42, stratify=y_q3)

q3_pipeline = Pipeline([
    ('preprocessor', q3_preprocessor),
    ('model',        RandomForestClassifier(n_estimators=100,
                                            class_weight='balanced',
                                            random_state=42))
])

q3_pipeline.fit(X_train, y_train)
print(classification_report(y_test, q3_pipeline.predict(X_test)))

# Save with churn probability
q3['churn_probability'] = q3_pipeline.predict_proba(X_q3)[:, 1]
q3['churn_risk'] = pd.cut(
    q3['churn_probability'],
    bins=[0, 0.33, 0.66, 1.0],
    labels=['Low', 'Medium', 'High']
)
q3.to_csv('q3_churn_predictions.csv')
print("✅ Saved q3_churn_predictions.csv\n")


# ══════════════════════════════════════════════
# QUESTION 4 — PRODUCT PORTFOLIO OPTIMIZATION
# ══════════════════════════════════════════════
print("=" * 50)
print("Q4: Product Portfolio Optimization")
print("=" * 50)

# Aggregate to product level
q4 = df.groupby(['product_name', 'category_name', 'brand_name']).agg(
    total_revenue  = ('revenue',   'sum'),     # numerical
    units_sold     = ('quantity',  'sum'),     # numerical
    avg_discount   = ('discount',  'mean'),    # numerical
    avg_list_price = ('list_price','mean'),    # numerical
    order_count    = ('order_id',  'nunique'), # numerical
).reset_index()

# Target: is this a HIGH VALUE product?
revenue_threshold = q4['total_revenue'].median()
q4['high_value']  = (q4['total_revenue'] > revenue_threshold).astype(int)

# Numerical → StandardScaler
q4_numerical = ['total_revenue', 'units_sold',
                 'avg_discount', 'avg_list_price', 'order_count']

# Nominal → OneHotEncoder
q4_nominal   = ['category_name', 'brand_name']

q4_preprocessor = ColumnTransformer(transformers=[
    ('num', StandardScaler(),
            q4_numerical),
    ('nom', OneHotEncoder(handle_unknown='ignore', sparse_output=False),
            q4_nominal),
], remainder='drop')

X_q4 = q4[q4_numerical + q4_nominal]
y_q4 = q4['high_value']

X_train, X_test, y_train, y_test = train_test_split(
    X_q4, y_q4, test_size=0.2, random_state=42)

q4_pipeline = Pipeline([
    ('preprocessor', q4_preprocessor),
    ('model',        RandomForestClassifier(n_estimators=100, random_state=42))
])

q4_pipeline.fit(X_train, y_train)
print(classification_report(y_test, q4_pipeline.predict(X_test)))

# Tag each product for dashboard
q4['stock_action'] = np.where(
    (q4['total_revenue'] > revenue_threshold) & (q4['avg_discount'] < 0.1),
    'REORDER NOW',
    np.where(
        (q4['total_revenue'] < revenue_threshold) & (q4['avg_discount'] > 0.15),
        'CONSIDER DROPPING',
        'MONITOR'
    )
)

q4.to_csv('q4_product_portfolio.csv')
print("✅ Saved q4_product_portfolio.csv\n")

print("🎉 All 3 models done! Load CSVs from outputs/ into Power BI.")



# # ── 1. Stock Action Distribution ──
# fig, ax = plt.subplots(figsize=(8, 4))
# q4['stock_action'].value_counts().plot(
#     kind='bar', ax=ax,
#     color=['#27ae60', '#e67e22', '#c0392b'])
# ax.set_title('Product Stock Action Recommendations', fontweight='bold')
# ax.set_ylabel('Number of Products')
# plt.xticks(rotation=0)
# plt.tight_layout()
# plt.savefig(os.path.join(OUT_DIR, 'q4_stock_actions.png'))
# plt.show(); plt.close()
# print("✅ Saved q4_stock_actions.png")

# # ── 2. Revenue vs Discount scatter (REORDER vs DROP) ──
# fig, ax = plt.subplots(figsize=(10, 6))
# colors = {'REORDER NOW': '#27ae60', 'MONITOR': '#f39c12', 'CONSIDER DROPPING': '#e74c3c'}
# for action, grp in q4.groupby('stock_action'):
#     ax.scatter(grp['avg_discount'], grp['total_revenue'],
#                label=action, alpha=0.7, color=colors[action], s=60)
# ax.set_title('Revenue vs Discount — Stock Decision Map', fontweight='bold')
# ax.set_xlabel('Avg Discount')
# ax.set_ylabel('Total Revenue ($)')
# ax.legend()
# plt.tight_layout()
# plt.savefig(os.path.join(OUT_DIR, 'q4_revenue_vs_discount.png'))
# plt.show(); plt.close()
# print("✅ Saved q4_revenue_vs_discount.png")

# # ── 3. Top 10 REORDER vs Bottom 10 DROP ──
# fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# reorder = q4[q4['stock_action'] == 'REORDER NOW'].nlargest(10, 'total_revenue')
# reorder.set_index('product_name')['total_revenue'].plot(
#     kind='barh', ax=axes[0], color='#27ae60')
# axes[0].set_title('Top 10 — REORDER NOW', fontweight='bold')
# axes[0].set_xlabel('Total Revenue ($)')

# drop = q4[q4['stock_action'] == 'CONSIDER DROPPING'].nsmallest(10, 'total_revenue')
# drop.set_index('product_name')['total_revenue'].plot(
#     kind='barh', ax=axes[1], color='#e74c3c')
# axes[1].set_title('Bottom 10 — CONSIDER DROPPING', fontweight='bold')
# axes[1].set_xlabel('Total Revenue ($)')

# plt.tight_layout()
# plt.savefig(os.path.join(OUT_DIR, 'q4_reorder_vs_drop.png'))
# plt.show(); plt.close()
# print("✅ Saved q4_reorder_vs_drop.png")

# # ── 4. Feature Importance ──
# q4_feature_names = (
#     q4_numerical
#     + list(q4_pipeline.named_steps['preprocessor']
#            .named_transformers_['nom']
#            .get_feature_names_out(q4_nominal))
# )
# q4_importances = pd.Series(
#     q4_pipeline.named_steps['model'].feature_importances_,
#     index=q4_feature_names
# ).nlargest(12).sort_values()

# fig, ax = plt.subplots(figsize=(10, 6))
# q4_importances.plot(kind='barh', ax=ax, color='#27ae60')
# ax.set_title('Q4 — Features Driving Product Value', fontweight='bold')
# ax.set_xlabel('Importance Score')
# plt.tight_layout()
# plt.savefig(os.path.join(OUT_DIR, 'q4_feature_importance.png'))
# plt.show(); plt.close()
# print("✅ Saved q4_feature_importance.png")

# q4.to_csv(os.path.join(OUT_DIR, 'q4_product_portfolio.csv'), index=False)
# print("✅ Saved q4_product_portfolio.csv\n")

# print("🎉 All models done! Import CSVs from outputs/ into Power BI.")
