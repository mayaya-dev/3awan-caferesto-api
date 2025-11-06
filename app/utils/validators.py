"""Validation functions for request data."""

def validate_required(data, field, field_type=None):
    """Validate that a required field exists and optionally check its type."""
    if field not in data:
        raise ValueError(f"{field} is required")
    if field_type and not isinstance(data[field], field_type):
        raise ValueError(f"{field} must be of type {field_type.__name__}")
    return data[field]

def validate_string(data, field, required=True, max_length=None):
    """Validate a string field."""
    if required:
        value = validate_required(data, field, str)
    else:
        value = data.get(field)
        if value is not None and not isinstance(value, str):
            raise ValueError(f"{field} must be a string")
    
    if value and max_length and len(value) > max_length:
        raise ValueError(f"{field} must be no longer than {max_length} characters")
    
    return value

def validate_number(data, field, required=True, min_value=None, max_value=None, field_type=float):
    """Validate a numeric field."""
    if required:
        try:
            value = field_type(validate_required(data, field))
        except (ValueError, TypeError):
            raise ValueError(f"{field} must be a valid number")
    else:
        try:
            value = field_type(data[field]) if field in data else None
        except (ValueError, TypeError):
            raise ValueError(f"{field} must be a valid number")
    
    if value is not None:
        if min_value is not None and value < min_value:
            raise ValueError(f"{field} must be at least {min_value}")
        if max_value is not None and value > max_value:
            raise ValueError(f"{field} must be no more than {max_value}")
    
    return value

def validate_foreign_key(data, field, model, required=True):
    """Validate a foreign key reference exists."""
    if required:
        value = validate_required(data, field, (int, str))
    else:
        value = data.get(field)
        if value is not None and not isinstance(value, (int, str)):
            raise ValueError(f"{field} must be a valid ID")
    
    if value is not None:
        # Query the referenced model
        instance = model.query.get(value)
        if not instance or getattr(instance, 'deleted_at', None) is not None:
            raise ValueError(f"Referenced {model.__name__} with id {value} not found")
    
    return value

def validate_enum(data, field, enum_class, required=True):
    """Validate an enum field."""
    if required:
        value = validate_required(data, field, str)
    else:
        value = data.get(field)
        if value is not None and not isinstance(value, str):
            raise ValueError(f"{field} must be a string")
    
    if value is not None:
        try:
            return enum_class(value)
        except ValueError:
            valid_values = [e.value for e in enum_class]
            raise ValueError(f"{field} must be one of: {', '.join(valid_values)}")
    return None

def validate_category_input(data):
    """Validate category creation/update input."""
    return {
        'category_name': validate_string(data, 'category_name', max_length=100)
    }

def validate_menu_input(data, partial=False):
    """Validate menu creation/update input."""
    from app.models.category import Category
    
    validated = {}
    required = not partial
    
    if 'menu_name' in data or required:
        validated['menu_name'] = validate_string(data, 'menu_name', required=required, max_length=100)
    if 'description' in data:
        validated['description'] = validate_string(data, 'description', required=False)
    if 'price' in data or required:
        validated['price'] = validate_number(data, 'price', required=required, min_value=0)
    if 'category_id' in data or required:
        validated['category_id'] = validate_foreign_key(data, 'category_id', Category, required=required)
    if 'image_url' in data:
        validated['image_url'] = validate_string(data, 'image_url', required=False, max_length=255)
    
    return validated

def validate_order_item_input(data, partial=False):
    """Validate order item creation/update input."""
    from app.models.menu import Menu
    from app.models.order import Order
    
    validated = {}
    required = not partial
    
    if 'order_id' in data or required:
        validated['order_id'] = validate_foreign_key(data, 'order_id', Order, required=required)
    if 'menu_id' in data or required:
        validated['menu_id'] = validate_foreign_key(data, 'menu_id', Menu, required=required)
    if 'quantity' in data or required:
        validated['quantity'] = validate_number(data, 'quantity', required=required, min_value=1, field_type=int)
    if 'price' in data:  # price is usually set from menu price
        validated['price'] = validate_number(data, 'price', required=False, min_value=0)
    
    return validated

def validate_order_item_for_create(data):
    """Validate an order item in the context of creating a new order.
    Requires menu_id and quantity; does NOT require order_id because it is set after the order is created.
    """
    from app.models.menu import Menu
    validated = {}
    # menu_id and quantity are required for creating order items via /orders
    validated['menu_id'] = validate_foreign_key(data, 'menu_id', Menu, required=True)
    validated['quantity'] = validate_number(data, 'quantity', required=True, min_value=1, field_type=int)
    # price optional; if omitted, controller will default from menu
    if 'price' in data:
        validated['price'] = validate_number(data, 'price', required=False, min_value=0)
    return validated

def validate_order_input(data, partial=False):
    """Validate order creation/update input."""
    validated = {}
    required = not partial
    
    # Optional customer_name on order
    customer_name = validate_string(data, 'customer_name', required=False, max_length=100)
    if customer_name is not None:
        validated['customer_name'] = customer_name
    
    if 'order_items' in data:
        items = data.get('order_items', [])
        if not isinstance(items, list):
            raise ValueError("order_items must be a list")
        
        validated_items = []
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("Each order item must be an object")
            # In the context of creating/updating an order, order_id is set by the controller.
            # Require menu_id and quantity for each item.
            validated_items.append(validate_order_item_for_create(item))
        validated['order_items'] = validated_items
    elif required:
        raise ValueError("order_items is required")
    
    return validated