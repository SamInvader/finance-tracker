from ..extensions import db
from ..models import Category, Transaction


def list_categories(user_id, kind=None):
    q = Category.query.filter_by(user_id=user_id)
    if kind:
        q = q.filter_by(kind=kind)
    return [c.to_dict() for c in q.order_by(Category.kind, Category.name).all()]


def create_category(user_id, data):
    if not data.get("name"):
        return None, {"name": "Name is required"}
    kind = data.get("kind") or "expense"
    if kind not in {"income", "expense"}:
        return None, {"kind": "Kind must be income or expense"}
    parent_id = data.get("parent_id")
    if parent_id and not Category.query.filter_by(id=parent_id, user_id=user_id).first():
        return None, {"parent_id": "Invalid parent category"}
    cat = Category(
        user_id=user_id,
        name=data["name"].strip(),
        kind=kind,
        icon=data.get("icon") or "circle",
        color=data.get("color") or "#0f766e",
        parent_id=parent_id,
    )
    db.session.add(cat)
    db.session.commit()
    return cat.to_dict(), None


def update_category(user_id, cat_id, data):
    cat = Category.query.filter_by(id=cat_id, user_id=user_id).first()
    if not cat:
        return None, "Category not found"
    if "name" in data and data["name"]:
        cat.name = data["name"].strip()
    if "icon" in data:
        cat.icon = data["icon"]
    if "color" in data:
        cat.color = data["color"]
    if "parent_id" in data:
        cat.parent_id = data["parent_id"]
    db.session.commit()
    return cat.to_dict(), None


def delete_category(user_id, cat_id):
    cat = Category.query.filter_by(id=cat_id, user_id=user_id).first()
    if not cat:
        return None, "Category not found"
    used = Transaction.query.filter_by(user_id=user_id, category_id=cat_id).count()
    if used:
        return None, "Cannot delete a category that is used by transactions"
    Category.query.filter_by(user_id=user_id, parent_id=cat_id).update({"parent_id": None})
    db.session.delete(cat)
    db.session.commit()
    return True, None
