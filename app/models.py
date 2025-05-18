from app import db

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(128), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    supplier = db.Column(db.String(128), nullable=False)
    reorder_level = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Inventory {self.item_name}>'

class Sales(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(128), nullable=False)
    sales_amount = db.Column(db.Float, nullable=False)
    sales_date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'<Sales {self.region} - {self.sales_date}>'
