from app.config.database import db
from datetime import datetime
from sqlalchemy import func

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.menu_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    deleted_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<OrderItem {self.order_item_id}>'
