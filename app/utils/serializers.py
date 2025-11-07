"""Helper functions for serializing models to dictionaries."""
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

def _serialize_datetime(value: Optional[datetime], tz_name: Optional[str] = None, tz_style: str = "offset"):
    """Serialize datetime with optional timezone conversion and formatting.
    - tz_name: e.g., "Asia/Jakarta" to convert from UTC to local.
    - tz_style: "offset" (default) yields "+HH:MM"; "z" yields "Z" when UTC.
    """
    if not value:
        return None
    try:
        # Convert timezone if requested
        if tz_name:
            try:
                tz = ZoneInfo(tz_name)
                value = value.astimezone(tz)
            except Exception:
                # Fallback: leave as-is if timezone unsupported
                pass
        s = value.isoformat()
        if tz_style == "z":
            # If datetime is UTC, replace "+00:00" with "Z"
            if value.tzinfo and value.utcoffset() == datetime.timedelta(0):
                s = s.replace("+00:00", "Z")
        return s
    except Exception:
        # Safe fallback
        return value.isoformat()

def model_to_dict(model, exclude_fields=None, tz_name: Optional[str] = None, tz_style: str = "offset"):
    """Convert a model instance to a dictionary with timezone-aware datetime serialization."""
    if exclude_fields is None:
        exclude_fields = set()
    
    data = {}
    for column in model.__table__.columns:
        if column.name not in exclude_fields:
            value = getattr(model, column.name)
            # Handle datetime values
            if isinstance(value, datetime):
                value = _serialize_datetime(value, tz_name=tz_name, tz_style=tz_style)
            data[column.name] = value
    return data

def serialize_category(category):
    """Serialize a Category model to a dictionary."""
    return model_to_dict(category)

def serialize_categories(categories):
    """Serialize a list of Category models."""
    return [serialize_category(c) for c in categories]

def serialize_menu(menu, tz_name: Optional[str] = None, tz_style: str = "offset"):
    """Serialize a Menu model to a dictionary."""
    data = model_to_dict(menu, tz_name=tz_name, tz_style=tz_style)
    if menu.category:
        data['category'] = serialize_category(menu.category)
    return data

def serialize_menus(menus):
    """Serialize a list of Menu models."""
    return [serialize_menu(m) for m in menus]

def serialize_order_item(order_item, tz_name: Optional[str] = None, tz_style: str = "offset"):
    """Serialize an OrderItem model to a dictionary."""
    data = model_to_dict(order_item, tz_name=tz_name, tz_style=tz_style)
    if order_item.menu:
        data['menu'] = serialize_menu(order_item.menu, tz_name=tz_name, tz_style=tz_style)
    return data

def serialize_order_items(order_items, tz_name: Optional[str] = None, tz_style: str = "offset"):
    """Serialize a list of OrderItem models."""
    return [serialize_order_item(oi, tz_name=tz_name, tz_style=tz_style) for oi in order_items]

def serialize_order(order, tz_name: Optional[str] = None, tz_style: str = "offset"):
    """Serialize an Order model to a dictionary."""
    data = model_to_dict(order, tz_name=tz_name, tz_style=tz_style)
    data['order_items'] = serialize_order_items(order.order_items, tz_name=tz_name, tz_style=tz_style)
    return data

def serialize_orders(orders, tz_name: Optional[str] = None, tz_style: str = "offset"):
    """Serialize a list of Order models."""
    return [serialize_order(o, tz_name=tz_name, tz_style=tz_style) for o in orders]