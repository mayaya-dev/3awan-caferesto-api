from app.models.menu import Menu
from app.models.category import Category
from app.config.database import SessionLocal
from app.utils.serializers import serialize_menu, serialize_menus
from flask import jsonify
from app.utils.validators import validate_menu_input
import datetime
import logging

logger = logging.getLogger("3awan.controllers.menu")


def get_all_menus(category_id=None):
    db = SessionLocal()
    try:
        # Base query: join Category and filter out soft-deleted entries
        query = (
            db.query(Menu)
            .join(Category, Menu.category_id == Category.category_id)
            .filter(
                Menu.deleted_at.is_(None),
                Category.deleted_at.is_(None)
            )
        )

        # Optional filtering by category_id when provided
        if category_id is not None:
            query = query.filter(Menu.category_id == category_id)

        menus = query.all()
        logger.info("Fetched menus", extra={"count": len(menus), "category_id": category_id})
        data = serialize_menus(menus)
        logger.info("Serialized menus", extra={"count": len(data)})
        return jsonify(data)
    except Exception as e:
        logger.exception("Failed to fetch menus")
        return {"error": str(e)}, 500
    finally:
        db.close()

def get_all_menu_list():
    db = SessionLocal()
    try:
        items = db.query(Menu).all()
        return jsonify(serialize_menus(items))
    except Exception as e:
        logger.exception("Failed to fetch menus")
        return {"error": str(e)}, 500
    finally:
        db.close()


def get_menu_by_id(menu_id: int):
    db = SessionLocal()
    try:
        menu = db.query(Menu).filter(
            Menu.menu_id == menu_id,
            Menu.deleted_at.is_(None)
        ).first()
        if not menu:
            return {"error": "Menu not found"}, 404
        return serialize_menu(menu)
    except Exception as e:
        logger.exception("Failed to fetch menu by id")
        return {"error": str(e)}, 500
    finally:
        db.close()


def create_menu(menu_data):
    try:
        validated = validate_menu_input(menu_data)
    except ValueError as e:
        return {"error": str(e)}, 400
    db = SessionLocal()
    try:
        menu = Menu(**validated)
        db.add(menu)
        db.commit()
        db.refresh(menu)
        logger.info("Created menu", extra={"menu_id": menu.menu_id})
        return serialize_menu(menu), 201
    except Exception as e:
        db.rollback()
        logger.exception("Failed to create menu")
        return {"error": str(e)}, 500
    finally:
        db.close()


def update_menu(menu_id: int, menu_data):
    db = SessionLocal()
    menu = db.query(Menu).filter(
        Menu.menu_id == menu_id,
        Menu.deleted_at.is_(None)
    ).first()
    if not menu:
        db.close()
        return {"error": "Menu not found"}, 404
    try:
        validated = validate_menu_input(menu_data, partial=True)
    except ValueError as e:
        db.close()
        return {"error": str(e)}, 400
    validated["updated_at"] = datetime.datetime.utcnow()
    try:
        for key, value in validated.items():
            setattr(menu, key, value)
        db.commit()
        db.refresh(menu)
        logger.info("Updated menu", extra={"menu_id": menu.menu_id})
        return serialize_menu(menu)
    except Exception as e:
        db.rollback()
        logger.exception("Failed to update menu")
        return {"error": str(e)}, 500
    finally:
        db.close()


def delete_menu(menu_id: int, type: int):
    db = SessionLocal()
    try:
        if type == 1:
            # Soft delete
            item = db.query(Menu).filter(
                Menu.menu_id == menu_id,
                Menu.deleted_at.is_(None)
            ).first()
            if not item:
                return {"error": "Menu not found"}, 404
            item.deleted_at = datetime.datetime.utcnow()
            db.commit()
            logger.info("Soft deleted menu", extra={"menu_id": menu_id})
            return {"detail": "Menu soft deleted"}
        elif type == 2:
            # Recovery soft delete
            item = db.query(Menu).filter(
                Menu.menu_id == menu_id,
                Menu.deleted_at.is_not(None)
            ).first()
            if not item:
                return {"error": "Menu not found or not deleted"}, 404
            item.deleted_at = None
            db.commit()
            logger.info("Recovered menu", extra={"menu_id": menu_id})
            return {"detail": "Menu recovered"}
        elif type == 3:
            # Hard delete (only if previously soft-deleted)
            item = db.query(Menu).filter(
                Menu.menu_id == menu_id,
                Menu.deleted_at.is_not(None)
            ).first()
            if not item:
                return {"error": "Menu not found or not soft-deleted"}, 404
            db.delete(item)
            db.commit()
            logger.info("Hard deleted menu", extra={"menu_id": menu_id})
            return {"detail": "Menu hard deleted"}
        else:
            return {"error": "Invalid delete type"}, 400
    except Exception as e:
        db.rollback()
        logger.exception("Failed to delete menu")
        return {"error": str(e)}, 500
    finally:
        db.close()


# Removed: get_menus_by_category in favor of category_id parameter in get_all_menus
