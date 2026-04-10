import pandas as pd
import numpy as np
import os
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Try to import statsmodels
try:
    from statsmodels.tsa.stattools import adfuller, acf, pacf
    STATS_AVAILABLE = True
    print("✅ statsmodels loaded successfully")
except ImportError:
    STATS_AVAILABLE = False
    print("⚠️  statsmodels not found. Install with: pip install statsmodels")

# ─────────────────────────────────────────────
# SETUP PATHS
# ─────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
OUT_DIR = os.path.join(BASE_DIR, 'outputs')
os.makedirs(OUT_DIR, exist_ok=True)

# Load data
path = os.path.join(BASE_DIR, 'sales_summary.csv')
df = pd.read_csv(path, parse_dates=['order_date'])

print("=" * 60)
print("📊 GENERATING POWER BI EXPORTS")
print("=" * 60)
print(f"📁 Input: {path}")
print(f"📁 Output: {OUT_DIR}")

# Prepare data
df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
df = df.sort_values(by='order_date')
df['month'] = df['order_date'].dt.month
df['quarter'] = df['order_date'].dt.quarter
df['day_of_week'] = df['order_date'].dt.dayofweek
df['year'] = df['order_date'].dt.year

# ══════════════════════════════════════════════
# Q2: REVENUE FORECASTING
# ══════════════════════════════════════════════
print("\n" + "=" * 60)
print("Q2: Revenue Forecasting")
print("=" * 60)

q2 = df.copy()
q2_numerical = ['quantity', 'discount', 'list_price', 'month', 'quarter', 'day_of_week', 'year']
q2_nominal = ['store_name', 'category_name', 'state']
q2_ordinal = ['order_status']
order_status_categories = [[1, 2, 3, 4]]

q2_preprocessor = ColumnTransformer(transformers=[
    ('num', StandardScaler(), q2_numerical),
    ('nom', OneHotEncoder(handle_unknown='ignore', sparse_output=False), q2_nominal),
    ('ord', OrdinalEncoder(categories=order_status_categories), q2_ordinal),
], remainder='drop')

X_q2 = q2[q2_numerical + q2_nominal + q2_ordinal]
y_q2 = q2['revenue']

tscv = TimeSeriesSplit(n_splits=5)
mae_scores = []
r2_scores = []

q2_pipeline = Pipeline([
    ('preprocessor', q2_preprocessor),
    ('model', RandomForestRegressor(n_estimators=100, random_state=42))
])

for train_index, test_index in tscv.split(X_q2):
    X_train, X_test = X_q2.iloc[train_index], X_q2.iloc[test_index]
    y_train, y_test = y_q2.iloc[train_index], y_q2.iloc[test_index]
    
    q2_pipeline.fit(X_train, y_train)
    y_pred_q2 = q2_pipeline.predict(X_test)
    
    mae_scores.append(mean_absolute_error(y_test, y_pred_q2))
    r2_scores.append(r2_score(y_test, y_pred_q2))

print(f"✅ Average MAE: ${sum(mae_scores)/len(mae_scores):,.2f}")
print(f"✅ Average R²: {sum(r2_scores)/len(r2_scores):.4f}")

# Save Q2 predictions
q2_results = X_test.copy()
# 🔧 FIX: Attach order_date back using original index (it was dropped by preprocessor)
q2_results['order_date'] = df.loc[X_test.index, 'order_date'].values
q2_results['actual_revenue'] = y_test.values
q2_results['predicted_revenue'] = y_pred_q2
q2_results.to_csv(os.path.join(OUT_DIR, 'q2_revenue_forecast.csv'), index=False)

# ── Q2 EXPORT 1: ADF Test ──
if STATS_AVAILABLE:
    q2_ts = df.groupby('order_date')['revenue'].sum().reset_index()
    q2_ts = q2_ts.sort_values('order_date').set_index('order_date')
    q2_ts = q2_ts.asfreq('D').ffill()
    
    adf_result = adfuller(q2_ts['revenue'].dropna())
    adf_df = pd.DataFrame({
        'Metric': ['ADF Statistic', 'p-value', 'Critical Value (1%)', 'Critical Value (5%)', 'Critical Value (10%)'],
        'Value': [adf_result[0], adf_result[1], adf_result[4]['1%'], adf_result[4]['5%'], adf_result[4]['10%']],
        'Is_Stationary': ['No', 'Yes if < 0.05', 'N/A', 'N/A', 'N/A']
    })
    adf_df.to_csv(os.path.join(OUT_DIR, 'q2_adf_test.csv'), index=False)
    print(f"✅ ADF Test: p-value = {adf_result[1]:.4f} → {'Stationary' if adf_result[1] < 0.05 else 'Non-Stationary'}")
    
    # ── Q2 EXPORT 2: ACF/PACF Values ──
    acf_vals = acf(q2_ts['revenue'].dropna(), nlags=30)
    pacf_vals = pacf(q2_ts['revenue'].dropna(), nlags=30, method='ywm')
    acf_pacf_df = pd.DataFrame({
        'lag': range(31),
        'acf_value': acf_vals,
        'pacf_value': pacf_vals
    })
    acf_pacf_df.to_csv(os.path.join(OUT_DIR, 'q2_acf_pacf.csv'), index=False)
    print("✅ Exported: q2_acf_pacf.csv")
else:
    print("⚠️  Skipping ADF/ACF/PACF exports (statsmodels not available)")

# ── Q2 EXPORT 3: Future Forecast ──
last_date = df['order_date'].max()
future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=30, freq='D')

future_df = pd.DataFrame({'order_date': future_dates})
future_df['month'] = future_df['order_date'].dt.month
future_df['quarter'] = future_df['order_date'].dt.quarter
future_df['day_of_week'] = future_df['order_date'].dt.dayofweek
future_df['year'] = future_df['order_date'].dt.year

for col in ['quantity', 'discount', 'list_price']:
    future_df[col] = df[col].median()
for col in ['store_name', 'category_name', 'state']:
    future_df[col] = df[col].mode().iloc[0] if not df[col].mode().empty else 'Unknown'
future_df['order_status'] = df['order_status'].mode().iloc[0] if not df['order_status'].mode().empty else 1

X_future = future_df[q2_numerical + q2_nominal + q2_ordinal]
future_df['predicted_revenue'] = q2_pipeline.predict(X_future)
future_df['prediction_type'] = 'forecast'

q2_forecast_viz = pd.concat([
    q2_results[['order_date', 'actual_revenue', 'predicted_revenue']].assign(type='actual'),
    future_df[['order_date', 'predicted_revenue']].assign(type='forecast', actual_revenue=np.nan)
], ignore_index=True)
q2_forecast_viz.to_csv(os.path.join(OUT_DIR, 'q2_forecast_viz.csv'), index=False)
print("✅ Exported: q2_forecast_viz.csv")

# ── Q2 EXPORT 4: Feature Importance ──
q2_feature_names = (
    q2_numerical 
    + list(q2_pipeline.named_steps['preprocessor'].named_transformers_['nom'].get_feature_names_out(q2_nominal))
    + q2_ordinal
)
q2_imp = pd.Series(
    q2_pipeline.named_steps['model'].feature_importances_,
    index=q2_feature_names
).sort_values(ascending=False).head(15).reset_index()
q2_imp.columns = ['feature', 'importance_score']
q2_imp.to_csv(os.path.join(OUT_DIR, 'q2_feature_importance.csv'), index=False)
print("✅ Exported: q2_feature_importance.csv")

print("✅ Q2 exports complete")

# ══════════════════════════════════════════════
# Q3: CUSTOMER CHURN
# ══════════════════════════════════════════════
print("\n" + "=" * 60)
print("Q3: Customer Churn")
print("=" * 60)

snapshot_date = df['order_date'].max()

q3 = df.groupby('customer_name').agg(
    total_orders=('order_id', 'nunique'),
    total_revenue=('revenue', 'sum'),
    avg_revenue=('revenue', 'mean'),
    avg_discount=('discount', 'mean'),
    avg_quantity=('quantity', 'mean'),
    days_since_order=('order_date', lambda x: (snapshot_date - x.max()).days),
    favourite_category=('category_name', lambda x: x.mode()[0] if not x.mode().empty else 'Unknown'),
    favourite_state=('state', lambda x: x.mode()[0] if not x.mode().empty else 'Unknown'),
).reset_index()

q3['churned'] = (q3['days_since_order'] > 365).astype(int)
print(f"📊 Churn rate: {q3['churned'].mean():.1%}")

q3_numerical = ['total_orders', 'total_revenue', 'avg_revenue', 'avg_discount', 'avg_quantity', 'days_since_order']
q3_nominal = ['favourite_category', 'favourite_state']

q3_preprocessor = ColumnTransformer(transformers=[
    ('num', StandardScaler(), q3_numerical),
    ('nom', OneHotEncoder(handle_unknown='ignore', sparse_output=False), q3_nominal),
], remainder='drop')

X_q3 = q3[q3_numerical + q3_nominal]
y_q3 = q3['churned']

X_train, X_test, y_train, y_test = train_test_split(X_q3, y_q3, test_size=0.2, random_state=42, stratify=y_q3)

q3_pipeline = Pipeline([
    ('preprocessor', q3_preprocessor),
    ('model', RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42))
])

q3_pipeline.fit(X_train, y_train)
print(classification_report(y_test, q3_pipeline.predict(X_test)))

q3['churn_probability'] = q3_pipeline.predict_proba(X_q3)[:, 1]
q3['churn_risk'] = pd.cut(q3['churn_probability'], bins=[0, 0.33, 0.66, 1.0], labels=['Low', 'Medium', 'High'])
q3.to_csv(os.path.join(OUT_DIR, 'q3_churn_predictions.csv'), index=False)

# ── Q3 EXPORT 1: High Risk Customers ──
high_risk = q3[q3['churn_risk'] == 'High'][[
    'customer_name', 'total_orders', 'total_revenue', 'avg_discount',
    'days_since_order', 'churn_probability', 'favourite_category', 'favourite_state'
]].copy()
high_risk['risk_reason'] = high_risk.apply(
    lambda row: 'No recent orders' if row['days_since_order'] > 365 
    else ('Low engagement' if row['total_orders'] < 3 else 'Multiple factors'),
    axis=1
)
high_risk.to_csv(os.path.join(OUT_DIR, 'q3_high_risk_customers.csv'), index=False)
print(f"✅ Exported {len(high_risk)} high-risk customers")

# ── Q3 EXPORT 2: Churn Drivers ──
q3_feature_names = (
    q3_numerical 
    + list(q3_pipeline.named_steps['preprocessor'].named_transformers_['nom'].get_feature_names_out(q3_nominal))
)
q3_imp = pd.Series(
    q3_pipeline.named_steps['model'].feature_importances_,
    index=q3_feature_names
).sort_values(ascending=False).head(12).reset_index()
q3_imp.columns = ['feature', 'importance_score']
q3_imp.to_csv(os.path.join(OUT_DIR, 'q3_churn_drivers.csv'), index=False)
print("✅ Exported: q3_churn_drivers.csv")

# ── Q3 EXPORT 3: Retention Playbook ──
retention_rules = pd.DataFrame({
    'trigger_condition': ['days_since_order > 180', 'churn_probability > 0.75', 'avg_discount > 0.2'],
    'recommended_action': ['Win-back email', 'Personal outreach', 'Bundle offer'],
    'priority': ['High', 'Critical', 'Medium']
})
retention_rules.to_csv(os.path.join(OUT_DIR, 'q3_retention_playbook.csv'), index=False)
print("✅ Exported: q3_retention_playbook.csv")

print("✅ Q3 exports complete")

# ══════════════════════════════════════════════
# Q4: PRODUCT PORTFOLIO
# ══════════════════════════════════════════════
print("\n" + "=" * 60)
print("Q4: Product Portfolio")
print("=" * 60)

q4 = df.groupby(['product_name', 'category_name', 'brand_name']).agg(
    total_revenue=('revenue', 'sum'),
    units_sold=('quantity', 'sum'),
    avg_discount=('discount', 'mean'),
    avg_list_price=('list_price', 'mean'),
    order_count=('order_id', 'nunique'),
).reset_index()

revenue_threshold = q4['total_revenue'].median()
q4['high_value'] = (q4['total_revenue'] > revenue_threshold).astype(int)

q4_numerical = ['total_revenue', 'units_sold', 'avg_discount', 'avg_list_price', 'order_count']
q4_nominal = ['category_name', 'brand_name']

q4_preprocessor = ColumnTransformer(transformers=[
    ('num', StandardScaler(), q4_numerical),
    ('nom', OneHotEncoder(handle_unknown='ignore', sparse_output=False), q4_nominal),
], remainder='drop')

X_q4 = q4[q4_numerical + q4_nominal]
y_q4 = q4['high_value']

X_train, X_test, y_train, y_test = train_test_split(X_q4, y_q4, test_size=0.2, random_state=42)

q4_pipeline = Pipeline([
    ('preprocessor', q4_preprocessor),
    ('model', RandomForestClassifier(n_estimators=100, random_state=42))
])

q4_pipeline.fit(X_train, y_train)
print(classification_report(y_test, q4_pipeline.predict(X_test)))

q4['stock_action'] = np.where(
    (q4['total_revenue'] > revenue_threshold) & (q4['avg_discount'] < 0.1), 'REORDER NOW',
    np.where((q4['total_revenue'] < revenue_threshold) & (q4['avg_discount'] > 0.15), 'CONSIDER DROPPING', 'MONITOR')
)

# ── Q4 EXPORT 1: Master Portfolio ──
q4_export = q4[[
    'product_name', 'category_name', 'brand_name', 'total_revenue', 'units_sold',
    'avg_discount', 'avg_list_price', 'order_count', 'stock_action', 'high_value'
]].copy()
q4_export['revenue_per_unit'] = q4_export['total_revenue'] / q4_export['units_sold'].replace(0, 1)
q4_export['restock_priority'] = (
    (q4_export['total_revenue'] / q4_export['total_revenue'].max()) * 0.4 +
    (1 - q4_export['avg_discount']) * 0.3 +
    (q4_export['order_count'] / q4_export['order_count'].max()) * 0.3
) * 100
q4_export.to_csv(os.path.join(OUT_DIR, 'q4_portfolio_master.csv'), index=False)
print("✅ Exported: q4_portfolio_master.csv")

# ── Q4 EXPORT 2: Reorder List ──
reorder_list = q4[q4['stock_action'] == 'REORDER NOW'][[
    'product_name', 'category_name', 'total_revenue', 'units_sold', 'avg_discount', 'order_count'
]].copy()
reorder_list['urgency_score'] = (
    reorder_list['total_revenue'].rank(pct=True) * 0.5 +
    (1 - reorder_list['avg_discount']).rank(pct=True) * 0.3 +
    reorder_list['order_count'].rank(pct=True) * 0.2
) * 100
reorder_list = reorder_list.sort_values('urgency_score', ascending=False)
reorder_list.to_csv(os.path.join(OUT_DIR, 'q4_reorder_priority.csv'), index=False)
print(f"✅ Exported {len(reorder_list)} reorder candidates")

# ── Q4 EXPORT 3: Drop List ──
drop_list = q4[q4['stock_action'] == 'CONSIDER DROPPING'][[
    'product_name', 'category_name', 'total_revenue', 'units_sold', 'avg_discount', 'order_count'
]].copy()
drop_list['drop_reason'] = np.where(
    drop_list['avg_discount'] > 0.15, 'High discount, low revenue',
    np.where(drop_list['order_count'] < 5, 'Low order frequency', 'Underperforming')
)
drop_list.to_csv(os.path.join(OUT_DIR, 'q4_drop_candidates.csv'), index=False)
print(f"✅ Exported {len(drop_list)} drop candidates")

# ── Q4 EXPORT 4: Decision Matrix ──
decision_data = q4[['product_name', 'total_revenue', 'avg_discount', 'stock_action', 'units_sold']].copy()
decision_data['bubble_size'] = decision_data['units_sold'] / decision_data['units_sold'].max() * 100
decision_data.to_csv(os.path.join(OUT_DIR, 'q4_decision_matrix.csv'), index=False)
print("✅ Exported: q4_decision_matrix.csv")

print("✅ Q4 exports complete")

# ══════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════
print("\n" + "=" * 60)
print("🎉 ALL EXPORTS COMPLETE!")
print("=" * 60)
print(f"\n📁 Files saved to: {OUT_DIR}")
print("\n📋 FILES GENERATED:")
print("Q2: q2_revenue_forecast.csv, q2_adf_test.csv, q2_acf_pacf.csv, q2_forecast_viz.csv, q2_feature_importance.csv")
print("Q3: q3_churn_predictions.csv, q3_high_risk_customers.csv, q3_churn_drivers.csv, q3_retention_playbook.csv")
print("Q4: q4_portfolio_master.csv, q4_reorder_priority.csv, q4_drop_candidates.csv, q4_decision_matrix.csv")
print("\n✅ NOW IMPORT THESE CSVs INTO POWER BI!")