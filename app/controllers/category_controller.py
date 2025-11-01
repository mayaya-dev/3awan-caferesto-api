from app.models.category import Category
from app.config.database import SessionLocal
from app.utils.serializers import serialize_category, serialize_categories
from flask import jsonify
from app.utils.validators import validate_category_input
import datetime
import logging

logger = logging.getLogger("3awan.controllers.category")


def get_all_categories():
    db = SessionLocal()
    try:
        items = db.query(Category).filter(Category.deleted_at.is_(None)).all()
        return jsonify(serialize_categories(items))
    except Exception as e:
        logger.exception("Failed to fetch categories")
        return {"error": str(e)}, 500
    finally:
        db.close()

def get_all_categories_list():
    db = SessionLocal()
    try:
        items = db.query(Category).all()
        return jsonify(serialize_categories(items))
    except Exception as e:
        logger.exception("Failed to fetch categories")
        return {"error": str(e)}, 500
    finally:
        db.close()

def get_category_by_id(cat_id: int):
    db = SessionLocal()
    try:
        item = db.query(Category).filter(
            Category.category_id == cat_id,
            Category.deleted_at.is_(None)
        ).first()
        if not item:
            return {"error": "Category not found"}, 404
        return serialize_category(item)
    except Exception as e:
        logger.exception("Failed to fetch category by id")
        return {"error": str(e)}, 500
    finally:
        db.close()


def create_category(data):
    try:
        validated = validate_category_input(data)
    except ValueError as e:
        return {"error": str(e)}, 400
    db = SessionLocal()
    try:
        item = Category(**validated)
        db.add(item)
        db.commit()
        db.refresh(item)
        logger.info("Created category", extra={"category_id": item.category_id})
        return serialize_category(item), 201
    except Exception as e:
        db.rollback()
        logger.exception("Failed to create category")
        return {"error": str(e)}, 500
    finally:
        db.close()


def update_category(cat_id: int, data):
    db = SessionLocal()
    item = db.query(Category).filter(
        Category.category_id == cat_id,
        Category.deleted_at.is_(None)
    ).first()
    if not item:
        db.close()
        return {"error": "Category not found"}, 404
    try:
        validated = validate_category_input(data)
    except ValueError as e:
        db.close()
        return {"error": str(e)}, 400
    validated["updated_at"] = datetime.datetime.utcnow()
    try:
        for k, v in validated.items():
            setattr(item, k, v)
        db.commit()
        db.refresh(item)
        logger.info("Updated category", extra={"category_id": item.category_id})
        return serialize_category(item)
    except Exception as e:
        db.rollback()
        logger.exception("Failed to update category")
        return {"error": str(e)}, 500
    finally:
        db.close()


def delete_category(cat_id: int, type: int):
    db = SessionLocal()
    try:
        if type == 1:
            # Soft delete
            item = db.query(Category).filter(
                Category.category_id == cat_id,
                Category.deleted_at.is_(None)
            ).first()
            if not item:
                return {"error": "Category not found"}, 404
            item.deleted_at = datetime.datetime.utcnow()
            db.commit()
            logger.info("Soft deleted category", extra={"category_id": item.category_id})
            return {"detail": "Category soft deleted"}
        elif type == 2:
            # Recovery soft delete
            item = db.query(Category).filter(
                Category.category_id == cat_id,
                Category.deleted_at.is_not(None)
            ).first()
            if not item:
                return {"error": "Category not found or not deleted"}, 404
            item.deleted_at = None
            db.commit()
            logger.info("Recovered category", extra={"category_id": item.category_id})
            return {"detail": "Category recovered"}
        elif type == 3:
            # Hard delete
            item = db.query(Category).filter(
                Category.category_id == cat_id,
                Category.deleted_at.is_not(None)
            ).first()
            if not item:
                return {"error": "Category not found or not soft-deleted"}, 404
            db.delete(item)
            db.commit()
            logger.info("Hard deleted category", extra={"category_id": cat_id})
            return {"detail": "Category hard deleted"}
        else:
            return {"error": "Invalid delete type"}, 400
    except Exception as e:
        db.rollback()
        logger.exception("Failed to delete category")
        return {"error": str(e)}, 500
    finally:
        db.close()
