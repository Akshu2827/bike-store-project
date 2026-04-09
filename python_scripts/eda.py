import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Hardcoded to your exact project directory
BASE_DIR = r'E:\Mostly_everything_related_to_coding_DS\business_case_studies\bike-store-project\bike-store-project'
CSV_PATH = os.path.join(BASE_DIR, 'sales_summary.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(CSV_PATH, parse_dates=['order_date'])
print(f"✅ Loaded {len(df):,} rows")
print(f"📁 Saving charts to: {OUTPUT_DIR}")

# 1. Monthly Revenue
fig, ax = plt.subplots(figsize=(12, 4))
monthly = df.groupby(df['order_date'].dt.to_period('M'))['revenue'].sum()
monthly.index = monthly.index.astype(str)
ax.plot(monthly.index, monthly.values, marker='o', color='steelblue')
ax.set_title('Monthly Revenue')
ax.set_ylabel('Revenue ($)')
ax.set_xlabel('Month')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'monthly_revenue.png'))
plt.show()
plt.close()
print("✅ Saved monthly_revenue.png")

# 2. Revenue by Store
fig, ax = plt.subplots(figsize=(8, 4))
df.groupby('store_name')['revenue'].sum().sort_values().plot(
    kind='barh', ax=ax, color='coral', title='Revenue by Store')
ax.set_xlabel('Revenue ($)')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'store_revenue.png'))
plt.show()
plt.close()
print("✅ Saved store_revenue.png")

# 3. Revenue by Category
fig, ax = plt.subplots(figsize=(8, 4))
df.groupby('category_name')['revenue'].sum().sort_values().plot(
    kind='bar', ax=ax, color='mediumpurple', title='Revenue by Category')
ax.set_ylabel('Revenue ($)')
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'category_revenue.png'))
plt.show()
plt.close()
print("✅ Saved category_revenue.png")

# 4. Top 10 Products
fig, ax = plt.subplots(figsize=(10, 5))
df.groupby('product_name')['revenue'].sum().nlargest(10).sort_values().plot(
    kind='barh', ax=ax, color='teal', title='Top 10 Products by Revenue')
ax.set_xlabel('Revenue ($)')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'top_products.png'))
plt.show()
plt.close()
print("✅ Saved top_products.png")

# 5. Revenue by Brand
fig, ax = plt.subplots(figsize=(8, 4))
df.groupby('brand_name')['revenue'].sum().sort_values().plot(
    kind='barh', ax=ax, color='goldenrod', title='Revenue by Brand')
ax.set_xlabel('Revenue ($)')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'brand_revenue.png'))
plt.show()
plt.close()
print("✅ Saved brand_revenue.png")

# 6. Revenue by State
fig, ax = plt.subplots(figsize=(8, 4))
df.groupby('state')['revenue'].sum().sort_values(ascending=False).plot(
    kind='bar', ax=ax, color='steelblue', title='Revenue by State')
ax.set_ylabel('Revenue ($)')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'state_revenue.png'))
plt.show()
plt.close()
print("✅ Saved state_revenue.png")

# 7. Top 10 Cities
fig, ax = plt.subplots(figsize=(10, 5))
df.groupby('city')['revenue'].sum().nlargest(10).sort_values().plot(
    kind='barh', ax=ax, color='salmon', title='Top 10 Cities by Revenue')
ax.set_xlabel('Revenue ($)')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'city_revenue.png'))
plt.show()
plt.close()
print("✅ Saved city_revenue.png")

# 8. Correlation Heatmap
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(df[['quantity', 'list_price', 'discount', 'revenue']].corr(),
            annot=True, cmap='coolwarm', ax=ax)
ax.set_title('Correlation Heatmap')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'correlation.png'))
plt.show()
plt.close()
print("✅ Saved correlation.png")

print(f"\n🎉 All charts saved to: {OUTPUT_DIR}")