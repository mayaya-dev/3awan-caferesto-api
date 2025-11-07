from app.models.order_item import OrderItem
from app.models.menu import Menu
from app.config.database import SessionLocal
from app.utils.serializers import serialize_order_item, serialize_order_items
from flask import jsonify, request
from app.utils.validators import validate_order_item_input
import datetime
import logging

logger = logging.getLogger("3awan.controllers.order_item")


def get_all_order_items():
    db = SessionLocal()
    try:
        items = db.query(OrderItem).filter(OrderItem.deleted_at.is_(None)).all()
        tz = request.args.get('tz')
        tz_style = request.args.get('tz_style', 'offset')
        return jsonify(serialize_order_items(items, tz_name=tz, tz_style=tz_style))
    except Exception as e:
        logger.exception("Failed to fetch order items")
        return {"error": str(e)}, 500
    finally:
        db.close()

def get_all_order_item_list():
    db = SessionLocal()
    try:
        items = db.query(OrderItem).all()
        tz = request.args.get('tz')
        tz_style = request.args.get('tz_style', 'offset')
        return jsonify(serialize_order_items(items, tz_name=tz, tz_style=tz_style))
    except Exception as e:
        logger.exception("Failed to fetch order items")
        return {"error": str(e)}, 500
    finally:
        db.close()

def get_order_item_by_id(item_id: int):
    db = SessionLocal()
    try:
        item = db.query(OrderItem).filter(
            OrderItem.order_item_id == item_id,
            OrderItem.deleted_at.is_(None)
        ).first()
        if not item:
            return {"error": "OrderItem not found"}, 404
        tz = request.args.get('tz')
        tz_style = request.args.get('tz_style', 'offset')
        return serialize_order_item(item, tz_name=tz, tz_style=tz_style)
    except Exception as e:
        logger.exception("Failed to fetch order item by id")
        return {"error": str(e)}, 500
    finally:
        db.close()


def create_order_item(data):
    try:
        validated = validate_order_item_input(data)
    except ValueError as e:
        return {"error": str(e)}, 400
    db = SessionLocal()
    try:
        # Default price from menu if not provided
        if "price" not in validated:
            menu = db.query(Menu).filter(Menu.menu_id == validated["menu_id"]).first()
            if not menu:
                db.close()
                return {"error": f"Menu id {validated['menu_id']} not found"}, 400
            validated["price"] = menu.price
        item = OrderItem(**validated)
        db.add(item)
        db.commit()
        db.refresh(item)
        logger.info("Created order_item", extra={"order_item_id": item.order_item_id})
        tz = request.args.get('tz')
        tz_style = request.args.get('tz_style', 'offset')
        return serialize_order_item(item, tz_name=tz, tz_style=tz_style), 201
    except Exception as e:
        db.rollback()
        logger.exception("Failed to create order_item")
        return {"error": str(e)}, 500
    finally:
        db.close()


def update_order_item(item_id: int, data):
    db = SessionLocal()
    item = db.query(OrderItem).filter(
        OrderItem.order_item_id == item_id,
        OrderItem.deleted_at.is_(None)
    ).first()
    if not item:
        db.close()
        return {"error": "OrderItem not found"}, 404
    try:
        validated = validate_order_item_input(data, partial=True)
    except ValueError as e:
        db.close()
        return {"error": str(e)}, 400
    validated["updated_at"] = datetime.datetime.utcnow()
    try:
        for k, v in validated.items():
            setattr(item, k, v)
        db.commit()
        db.refresh(item)
        logger.info("Updated order_item", extra={"order_item_id": item.order_item_id})
        tz = request.args.get('tz')
        tz_style = request.args.get('tz_style', 'offset')
        return serialize_order_item(item, tz_name=tz, tz_style=tz_style)
    except Exception as e:
        db.rollback()
        logger.exception("Failed to update order_item")
        return {"error": str(e)}, 500
    finally:
        db.close()


def delete_order_item(item_id: int):
    db = SessionLocal()
    item = db.query(OrderItem).filter(
        OrderItem.order_item_id == item_id,
        OrderItem.deleted_at.is_(None)
    ).first()
    if not item:
        db.close()
        return {"error": "OrderItem not found"}, 404
    try:
        item.deleted_at = datetime.datetime.utcnow()
        db.commit()
        logger.info("Deleted order_item", extra={"order_item_id": item.order_item_id})
        return {"detail": "OrderItem deleted"}
    except Exception as e:
        db.rollback()
        logger.exception("Failed to delete order_item")
        return {"error": str(e)}, 500
    finally:
        db.close()
