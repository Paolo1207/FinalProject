from app import create_app, db
from app.models import Sales, Inventory
import random
from datetime import datetime, timedelta

app = create_app()  # your app factory function

with app.app_context():
    # Optional: clear tables (be cautious!)
    # db.session.query(Sales).delete()
    # db.session.query(Inventory).delete()
    # db.session.commit()

    # Dummy data lists
    items = ['Rice A', 'Rice B', 'Rice C', 'Rice D']
    regions = ['Region 1', 'Region 2', 'Region 3', 'Region 4']
    suppliers = ['Supplier X', 'Supplier Y', 'Supplier Z']  # added suppliers list

    # Insert dummy inventory (4 items)
    for item in items:
        inv = Inventory(
            item_name=item,
            quantity=random.randint(50, 500),
            price=round(random.uniform(20, 50), 2),
            supplier=random.choice(suppliers),  # supply a valid non-null value
            reorder_level=100
        )
        db.session.add(inv)
    db.session.commit()

    # Insert dummy sales (100 records)
    start_date = datetime.now() - timedelta(days=180)  # last 6 months

    for _ in range(100):
        sale = Sales(
            sales_date=start_date + timedelta(days=random.randint(0, 180)),
            region=random.choice(regions),
            sales_amount=round(random.uniform(1000, 10000), 2)
        )
        db.session.add(sale)

    db.session.commit()

    print("Inserted 100 dummy sales and some inventory records.")
