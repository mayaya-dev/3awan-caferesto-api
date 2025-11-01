from app.config.database import db
# Ensure OrderItem class is imported so SQLAlchemy can resolve the relationship string
from app.models.order_item import OrderItem
from datetime import datetime
from sqlalchemy import func

class Menu(db.Model):
    __tablename__ = 'menus'
    
    menu_id = db.Column(db.Integer, primary_key=True)
    menu_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    deleted_at = db.Column(db.DateTime)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='menu', lazy=True)
    
    def __repr__(self):
        return f'<Menu {self.menu_name}>'
