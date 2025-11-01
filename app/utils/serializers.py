"""Helper functions for serializing models to dictionaries."""
from datetime import datetime
from app.models.order import OrderStatus

def model_to_dict(model, exclude_fields=None):
    """Convert a model instance to a dictionary."""
    if exclude_fields is None:
        exclude_fields = set()
    
    data = {}
    for column in model.__table__.columns:
        if column.name not in exclude_fields:
            value = getattr(model, column.name)
            # Handle enum values
            if isinstance(value, OrderStatus):
                value = value.value
            # Handle datetime values
            elif isinstance(value, datetime):
                value = value.isoformat() if value else None
            data[column.name] = value
    return data

def serialize_category(category):
    """Serialize a Category model to a dictionary."""
    return model_to_dict(category)

def serialize_categories(categories):
    """Serialize a list of Category models."""
    return [serialize_category(c) for c in categories]

def serialize_menu(menu):
    """Serialize a Menu model to a dictionary."""
    data = model_to_dict(menu)
    if menu.category:
        data['category'] = serialize_category(menu.category)
    return data

def serialize_menus(menus):
    """Serialize a list of Menu models."""
    return [serialize_menu(m) for m in menus]

def serialize_order_item(order_item):
    """Serialize an OrderItem model to a dictionary."""
    data = model_to_dict(order_item)
    if order_item.menu:
        data['menu'] = serialize_menu(order_item.menu)
    return data

def serialize_order_items(order_items):
    """Serialize a list of OrderItem models."""
    return [serialize_order_item(oi) for oi in order_items]

def serialize_order(order):
    """Serialize an Order model to a dictionary."""
    data = model_to_dict(order)
    data['order_items'] = serialize_order_items(order.order_items)
    return data

def serialize_orders(orders):
    """Serialize a list of Order models."""
    return [serialize_order(o) for o in orders]