"""Create demo user with realistic Nigerian sample data. Isolated from other users."""
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app
from app.extensions import db
from app.models import (
    Account,
    Bill,
    Budget,
    BudgetCategory,
    Category,
    Debt,
    RecurringTransaction,
    SavingsGoal,
    Subscription,
    User,
)
from app.services.defaults import seed_user_defaults
from app.services.transactions import create_transaction
from app.utils.dates import month_key
from app.utils.money import to_minor


def seed():
    app = create_app()
    with app.app_context():
        email = "demo@ledgerly.local"
        user = User.query.filter_by(email=email).first()
        if user:
            print("Demo user already exists:", email)
            return
        user = User(email=email, name="Demo User", is_demo=True)
        user.set_password("DemoPass123!")
        db.session.add(user)
        db.session.flush()
        seed_user_defaults(user)
        db.session.commit()

        # Replace default cash with named accounts
        Account.query.filter_by(user_id=user.id).delete()
        cash = Account(user_id=user.id, name="Cash", type="cash", balance_minor=0, currency="NGN")
        opay = Account(user_id=user.id, name="OPay", type="wallet", institution="OPay", balance_minor=0, currency="NGN")
        monie = Account(user_id=user.id, name="Moniepoint", type="wallet", institution="Moniepoint", balance_minor=0, currency="NGN")
        bank = Account(user_id=user.id, name="GTBank", type="bank", institution="Guaranty Trust Bank", balance_minor=0, currency="NGN")
        savings = Account(user_id=user.id, name="Savings", type="savings", institution="GTBank", balance_minor=0, currency="NGN")
        db.session.add_all([cash, opay, monie, bank, savings])
        db.session.commit()

        cats = {c.name: c for c in Category.query.filter_by(user_id=user.id).all()}
        today = date.today()

        def tx(days_ago, amount, typ, account, cat, desc):
            create_transaction(
                user.id,
                {
                    "type": typ,
                    "amount": amount,
                    "account_id": account.id,
                    "category_id": cats[cat].id if cat else None,
                    "date": (today - timedelta(days=days_ago)).isoformat(),
                    "description": desc,
                    "tags": "demo",
                },
            )

        tx(40, 250000, "income", bank, "Salary", "August salary")
        tx(10, 250000, "income", bank, "Salary", "September salary")
        tx(8, 20000, "income", opay, "Freelance", "Design gig")
        tx(35, 80000, "expense", bank, "Rent", "Room rent")
        tx(5, 80000, "expense", bank, "Rent", "Room rent")
        tx(3, 4500, "expense", opay, "Food & Groceries", "Shoprite groceries")
        tx(2, 1800, "expense", cash, "Food & Groceries", "Lunch")
        tx(1, 3500, "expense", opay, "Transport", "Bolt to campus")
        tx(0, 2200, "expense", monie, "Data & Airtime", "MTN data")
        tx(6, 15000, "expense", opay, "Education", "Course materials")
        tx(4, 5000, "expense", bank, "Giving", "Church offering")
        create_transaction(
            user.id,
            {
                "type": "transfer",
                "amount": 40000,
                "account_id": bank.id,
                "destination_account_id": savings.id,
                "date": today.isoformat(),
                "description": "Transfer to savings",
            },
        )

        budget = Budget(user_id=user.id, month=month_key(today), overall_limit_minor=to_minor(200000))
        db.session.add(budget)
        db.session.flush()
        db.session.add_all(
            [
                BudgetCategory(budget_id=budget.id, category_id=cats["Food & Groceries"].id, amount_minor=to_minor(50000)),
                BudgetCategory(budget_id=budget.id, category_id=cats["Transport"].id, amount_minor=to_minor(30000)),
                BudgetCategory(budget_id=budget.id, category_id=cats["Data & Airtime"].id, amount_minor=to_minor(10000)),
                BudgetCategory(budget_id=budget.id, category_id=cats["Entertainment"].id, amount_minor=to_minor(15000)),
            ]
        )
        db.session.add(
            SavingsGoal(
                user_id=user.id,
                account_id=savings.id,
                name="Emergency Fund",
                target_minor=to_minor(300000),
                current_minor=to_minor(40000),
                deadline=today + timedelta(days=180),
                description="DEMO: 3 months of expenses",
                icon="shield",
                priority=1,
            )
        )
        db.session.add(
            SavingsGoal(
                user_id=user.id,
                name="New Laptop",
                target_minor=to_minor(450000),
                current_minor=to_minor(25000),
                deadline=today + timedelta(days=240),
                icon="laptop",
                priority=2,
            )
        )
        db.session.add(
            Bill(
                user_id=user.id,
                name="Electricity (PHCN)",
                amount_minor=to_minor(8500),
                due_date=today + timedelta(days=4),
                frequency="monthly",
                category_id=cats["Bills"].id,
                account_id=opay.id,
            )
        )
        db.session.add(
            Subscription(
                user_id=user.id,
                name="Spotify",
                amount_minor=to_minor(1800),
                billing_cycle="monthly",
                next_billing_date=today + timedelta(days=9),
                category_id=cats["Subscriptions"].id,
                account_id=opay.id,
            )
        )
        db.session.add(
            RecurringTransaction(
                user_id=user.id,
                account_id=bank.id,
                category_id=cats["Salary"].id,
                type="income",
                amount_minor=to_minor(250000),
                description="Salary",
                frequency="monthly",
                interval=1,
                start_date=today.replace(day=1),
                next_occurrence=today.replace(day=28) if today.day < 28 else today + timedelta(days=20),
                is_active=True,
            )
        )
        db.session.add(
            Debt(
                user_id=user.id,
                name="Laptop hire-purchase",
                lender="Friend",
                original_minor=to_minor(120000),
                remaining_minor=to_minor(45000),
                interest_rate_bps=0,
                minimum_payment_minor=to_minor(15000),
                due_date=today + timedelta(days=12),
                notes="DEMO DATA — not a real loan",
            )
        )
        db.session.commit()
        print("Seeded demo user demo@ledgerly.local / DemoPass123!")


if __name__ == "__main__":
    seed()
