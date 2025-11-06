from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu import Menu
from app.config.database import SessionLocal
from app.utils.serializers import serialize_order, serialize_orders
from flask import jsonify
from app.utils.validators import validate_order_input
import datetime
import logging

logger = logging.getLogger("3awan.controllers.order")


def get_all_orders():
    db = SessionLocal()
    try:
        items = db.query(Order).filter(Order.deleted_at.is_(None)).all()
        return jsonify(serialize_orders(items))
    except Exception as e:
        logger.exception("Failed to fetch orders")
        return {"error": str(e)}, 500
    finally:
        db.close()

def get_all_order_list():
    db = SessionLocal()
    try:
        items = db.query(Order).all()
        return jsonify(serialize_orders(items))
    except Exception as e:
        logger.exception("Failed to fetch orders")
        return {"error": str(e)}, 500
    finally:
        db.close()

def get_order_by_id(order_id: int):
    db = SessionLocal()
    try:
        item = db.query(Order).filter(
            Order.order_id == order_id,
            Order.deleted_at.is_(None)
        ).first()
        if not item:
            return {"error": "Order not found"}, 404
        return serialize_order(item)
    except Exception as e:
        logger.exception("Failed to fetch order by id")
        return {"error": str(e)}, 500
    finally:
        db.close()


def create_order(data):
    try:
        validated = validate_order_input(data)
    except ValueError as e:
        return {"error": str(e)}, 400
    order_items_data = validated.pop("order_items", [])
    customer_name = validated.get("customer_name")
    db = SessionLocal()
    try:
        order = Order(order_date=datetime.datetime.utcnow(), customer_name=customer_name)
        db.add(order)
        db.commit()
        db.refresh(order)
        # create order items
        for it in order_items_data:
            # default price from menu if not provided
            if "price" not in it:
                menu = db.query(Menu).filter(Menu.menu_id == it["menu_id"]).first()
                if not menu:
                    db.close()
                    return {"error": f"Menu id {it['menu_id']} not found"}, 400
                it["price"] = menu.price
            oi = OrderItem(
                order_id=order.order_id,
                menu_id=it["menu_id"],
                quantity=it["quantity"],
                price=it["price"],
            )
            db.add(oi)
        db.commit()
        db.refresh(order)
        logger.info("Created order", extra={"order_id": order.order_id})
        return serialize_order(order), 201
    except Exception as e:
        db.rollback()
        logger.exception("Failed to create order")
        return {"error": str(e)}, 500
    finally:
        db.close()


def update_order(order_id: int, data):
    db = SessionLocal()
    order = db.query(Order).filter(
        Order.order_id == order_id,
        Order.deleted_at.is_(None)
    ).first()
    if not order:
        db.close()
        return {"error": "Order not found"}, 404
    try:
        validated = validate_order_input(data, partial=True)
    except ValueError as e:
        db.close()
        return {"error": str(e)}, 400
    validated["updated_at"] = datetime.datetime.utcnow()
    try:
        if "status" in validated and validated["status"] is not None:
            order.status = validated["status"]
        if "order_items" in validated:
            # clear and replace order items
            now = datetime.datetime.utcnow()
            db.query(OrderItem).filter(OrderItem.order_id == order.order_id).update({"deleted_at": now})
            for it in validated["order_items"]:
                if "price" not in it:
                    menu = db.query(Menu).filter(Menu.menu_id == it["menu_id"]).first()
                    if not menu:
                        db.close()
                        return {"error": f"Menu id {it['menu_id']} not found"}, 400
                    it["price"] = menu.price
                oi = OrderItem(
                    order_id=order.order_id,
                    menu_id=it["menu_id"],
                    quantity=it["quantity"],
                    price=it["price"],
                )
                db.add(oi)
        db.commit()
        db.refresh(order)
        logger.info("Updated order", extra={"order_id": order.order_id})
        return serialize_order(order)
    except Exception as e:
        db.rollback()
        logger.exception("Failed to update order")
        return {"error": str(e)}, 500
    finally:
        db.close()


def delete_order(order_id: int):
    db = SessionLocal()
    order = db.query(Order).filter(
        Order.order_id == order_id,
        Order.deleted_at.is_(None)
    ).first()
    if not order:
        db.close()
        return {"error": "Order not found"}, 404
    try:
        now = datetime.datetime.utcnow()
        order.deleted_at = now
        db.query(OrderItem).filter(OrderItem.order_id == order.order_id).update({"deleted_at": now})
        db.commit()
        logger.info("Deleted order", extra={"order_id": order.order_id})
        return {"detail": "Order deleted"}
    except Exception as e:
        db.rollback()
        logger.exception("Failed to delete order")
        return {"error": str(e)}, 500
    finally:
        db.close()
