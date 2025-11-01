from app.config.database import db
# Ensure Menu class is imported so SQLAlchemy can resolve the relationship string
from app.models.menu import Menu
from datetime import datetime
from sqlalchemy import func

class Category(db.Model):
    __tablename__ = 'categories'
    
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    deleted_at = db.Column(db.DateTime)
    
    # Relationships
    menus = db.relationship('Menu', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.category_name}>'
