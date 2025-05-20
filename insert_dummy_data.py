import sqlite3
import random
from datetime import datetime, timedelta

# Connect to your SQLite DB (adjust path as needed)
conn = sqlite3.connect('instance/rice_inventory.db')
cursor = conn.cursor()

# --- Generate and insert inventory data ---

# Inventory columns: id, item_name, quantity, price, supplier, reorder_level

suppliers = ['Supplier A', 'Supplier B', 'Supplier C', 'Supplier D']
items = [f'Rice Variant {i}' for i in range(1, 501)]  # 500 items total

for item in items:
    quantity = random.randint(50, 500)
    price = round(random.uniform(20.0, 50.0), 2)
    supplier = random.choice(suppliers)
    reorder_level = random.randint(20, 100)
    
    cursor.execute('''
        INSERT INTO inventory (item_name, quantity, price, supplier, reorder_level)
        VALUES (?, ?, ?, ?, ?)
    ''', (item, quantity, price, supplier, reorder_level))

print("Inserted inventory dummy data.")

# --- Generate and insert sales data ---

# Sales columns: id, sales_date, region, sales_amount, item_name
regions = ['North', 'South', 'East', 'West', 'Central']

start_date = datetime.now() - timedelta(days=365)  # 1 year ago
num_sales_records = 1000

for _ in range(num_sales_records):
    sales_date = start_date + timedelta(days=random.randint(0, 365))
    region = random.choice(regions)
    sales_amount = round(random.uniform(1000, 10000), 2)
    
    cursor.execute('''
        INSERT INTO sales (sales_date, region, sales_amount)
        VALUES (?, ?, ?)
    ''', (sales_date.strftime('%Y-%m-%d'), region, sales_amount))

print("Inserted sales dummy data.")

conn.commit()
conn.close()
