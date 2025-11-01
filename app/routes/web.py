from flask import Blueprint, request
import logging

# Import entity-specific controllers
from app.controllers.category_controller import (
    get_all_categories_list, get_all_categories, get_category_by_id, create_category, update_category, delete_category,
)
from app.controllers.menu_controller import (
    get_all_menu_list, get_all_menus, get_menu_by_id, create_menu, update_menu, delete_menu,
)
from app.controllers.order_controller import (
    get_all_order_list, get_all_orders, get_order_by_id, create_order, update_order, delete_order,
)
from app.controllers.order_item_controller import (
    get_all_order_item_list, get_all_order_items, get_order_item_by_id, create_order_item, update_order_item, delete_order_item,
)
from app.config.database import SessionLocal
from app.models.menu import Menu
from app.utils.serializers import serialize_menus

# Define a single blueprint 'web'
web = Blueprint("web", __name__, url_prefix="/api")

# Setup logger for API routes
logger = logging.getLogger("3awan.api")


@web.errorhandler(Exception)
def api_error_handler(e):
    # Ensure any uncaught exceptions in API routes are logged and returned as JSON
    logger.exception("Unhandled exception in API route")
    return {"error": str(e)}, 500


@web.route('/')
def index():
    return "3awan CafeResto API"


# Categories
@web.route('/categories', methods=['GET'])
def categories_list():
    try:
        return get_all_categories()
    except Exception as e:
        logger.exception("Error in categories_list route")
        return {"error": str(e)}, 500

@web.route('/categories/all', methods=['GET'])
def categories_all_list():
    return get_all_categories_list()


@web.route('/categories/<int:category_id>', methods=['GET'])
def categories_get(category_id):
    return get_category_by_id(category_id)


@web.route('/categories', methods=['POST'])
def categories_post():
    return create_category(request.get_json() or {})


@web.route('/categories/<int:category_id>', methods=['PUT'])
def categories_put(category_id):
    return update_category(category_id, request.get_json() or {})


@web.route('/categories/<int:category_id>/<int:type>', methods=['DELETE'])
def categories_delete(category_id, type):
    return delete_category(category_id, type)


# Menus
@web.route('/menus', methods=['GET'])
def menus_list():
    try:
        # Optional query param to filter by category: /api/menus?category_id=6
        category_id = request.args.get('category_id', type=int)
        return get_all_menus(category_id)
    except Exception as e:
        logger.exception("Error in menus_list route")
        return {"error": str(e)}, 500


@web.route('/menus/all', methods=['GET'])
def menus_all_list():
    return get_all_menu_list()

# Diagnostic route to isolate DB + serialization directly in route
@web.route('/menus_diag', methods=['GET'])
def menus_diag():
    try:
        s = SessionLocal()
        try:
            menus = s.query(Menu).filter(Menu.deleted_at.is_(None)).all()
            return serialize_menus(menus), 200
        finally:
            s.close()
    except Exception as e:
        logger.exception("Error in menus_diag")
        return {"error": str(e)}, 500

# Simple diagnostic route to verify routing works
@web.route('/menus_static', methods=['GET'])
def menus_static():
    return [], 200


@web.route('/menus/<int:menu_id>', methods=['GET'])
def menus_get(menu_id):
    return get_menu_by_id(menu_id)


@web.route('/menus', methods=['POST'])
def menus_post():
    return create_menu(request.get_json() or {})


@web.route('/menus/<int:menu_id>', methods=['PUT'])
def menus_put(menu_id):
    return update_menu(menu_id, request.get_json() or {})


@web.route('/menus/<int:menu_id>/<int:type>', methods=['DELETE'])
def menus_delete(menu_id, type):
    return delete_menu(menu_id, type)


# Removed explicit /categories/<id>/menus route in favor of /api/menus?category_id=<id>


# Orders
@web.route('/orders', methods=['GET'])
def orders_list():
    return get_all_orders()

@web.route('/orders/all', methods=['GET'])
def orders_all_list():
    return get_all_order_list()


@web.route('/orders/<int:order_id>', methods=['GET'])
def orders_get(order_id):
    return get_order_by_id(order_id)


@web.route('/orders', methods=['POST'])
def orders_post():
    return create_order(request.get_json() or {})


@web.route('/orders/<int:order_id>', methods=['PUT'])
def orders_put(order_id):
    return update_order(order_id, request.get_json() or {})


@web.route('/orders/<int:order_id>', methods=['DELETE'])
def orders_delete(order_id):
    return delete_order(order_id)


# Order Items
@web.route('/order_items', methods=['GET'])
def order_items_list():
    return get_all_order_items()

@web.route('/order_items/all', methods=['GET'])
def order_items_all_list():
    return get_all_order_item_list()

@web.route('/order_items/<int:order_item_id>', methods=['GET'])
def order_items_get(order_item_id):
    return get_order_item_by_id(order_item_id)


@web.route('/order_items', methods=['POST'])
def order_items_post():
    return create_order_item(request.get_json() or {})


@web.route('/order_items/<int:order_item_id>', methods=['PUT'])
def order_items_put(order_item_id):
    return update_order_item(order_item_id, request.get_json() or {})


@web.route('/order_items/<int:order_item_id>', methods=['DELETE'])
def order_items_delete(order_item_id):
    return delete_order_item(order_item_id)
