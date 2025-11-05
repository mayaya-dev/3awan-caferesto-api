from app.config.database import db
# Ensure OrderItem class is imported so SQLAlchemy can resolve the relationship string
from app.models.order_item import OrderItem
from datetime import datetime
from sqlalchemy import func

class Order(db.Model):
    __tablename__ = 'orders'
    
    order_id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    deleted_at = db.Column(db.DateTime)
    
    # Relationships
    # cascade so that when an Order is added/removed the related OrderItems follow
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_id}>'
