from ..models import Category

DEFAULT_EXPENSE = [
    ("Food & Groceries", "utensils", "#0f766e"),
    ("Transport", "bus", "#0369a1"),
    ("Data & Airtime", "smartphone", "#7c3aed"),
    ("Education", "graduation-cap", "#b45309"),
    ("Bills", "receipt", "#be123c"),
    ("Rent", "home", "#9f1239"),
    ("Family Support", "users", "#0e7490"),
    ("Health", "heart-pulse", "#e11d48"),
    ("Entertainment", "film", "#c026d3"),
    ("Shopping", "shopping-bag", "#ea580c"),
    ("Subscriptions", "repeat", "#4f46e5"),
    ("Personal Care", "sparkles", "#db2777"),
    ("Giving", "hand-heart", "#15803d"),
    ("Savings", "piggy-bank", "#047857"),
    ("Other", "circle", "#64748b"),
]

DEFAULT_INCOME = [
    ("Salary", "briefcase", "#059669"),
    ("Allowance", "wallet", "#0d9488"),
    ("Freelance", "laptop", "#2563eb"),
    ("Business", "store", "#7c3aed"),
    ("Gift", "gift", "#db2777"),
    ("Other", "circle", "#64748b"),
]


def seed_user_defaults(user):
    from ..extensions import db
    from ..models import Account, UserPreference

    if not user.preference:
        db.session.add(
            UserPreference(
                user_id=user.id,
                currency="NGN",
                locale="en-NG",
                theme="system",
            )
        )

    if Category.query.filter_by(user_id=user.id).count() == 0:
        for name, icon, color in DEFAULT_EXPENSE:
            db.session.add(
                Category(user_id=user.id, name=name, kind="expense", icon=icon, color=color)
            )
        for name, icon, color in DEFAULT_INCOME:
            db.session.add(
                Category(user_id=user.id, name=name, kind="income", icon=icon, color=color)
            )

    if Account.query.filter_by(user_id=user.id).count() == 0:
        db.session.add(
            Account(
                user_id=user.id,
                name="Cash",
                type="cash",
                institution="",
                balance_minor=0,
                currency="NGN",
            )
        )
