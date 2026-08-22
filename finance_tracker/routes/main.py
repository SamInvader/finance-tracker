from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from finance_tracker.data_access import (
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES,
    add_transaction,
    create_savings_goal,
    delete_transaction as delete_txn,
    get_all_months,
    get_budget_for_month,
    get_monthly_expense_by_category,
    get_monthly_summary,
    get_savings_goals,
    get_transaction_by_id,
    get_transactions,
    save_budget,
    update_savings_goal,
    update_transaction,
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/home")
def home_page():
    return render_template("home.html")


@main_bp.route("/")
def index():
    current_month = datetime.today().strftime("%Y-%m")
    all_transactions = get_transactions()

    monthly_transactions = [t for t in all_transactions if t["date"].startswith(current_month)]
    total_income = sum(float(t["amount"]) for t in monthly_transactions if t["type"] == "income")
    total_expenses = sum(float(t["amount"]) for t in monthly_transactions if t["type"] == "expense")

    budget_record = get_budget_for_month(current_month) or {"amount": 0.0}
    budget_amount = float(budget_record.get("amount", 0.0))
    remaining_budget = budget_amount - total_expenses
    budget_used = (total_expenses / budget_amount * 100) if budget_amount else 0.0

    savings = sum(float(goal["current_amount"]) for goal in get_savings_goals())
    recent_transactions = get_transactions()[:6]

    category_totals = {}
    for txn in monthly_transactions:
        if txn["type"] == "expense":
            category_totals[txn["category"]] = category_totals.get(txn["category"], 0.0) + float(txn["amount"])

    history = []
    income_series = []
    expense_series = []
    for month in sorted({txn["date"][:7] for txn in all_transactions} or [current_month]):
        summary = get_monthly_summary(month)
        history.append(month)
        income_series.append(float(summary.get("income", 0.0)))
        expense_series.append(float(summary.get("expense", 0.0)))

    if not history:
        history = [current_month]
        income_series = [0.0]
        expense_series = [0.0]

    return render_template(
        "dashboard.html",
        balance=total_income - total_expenses,
        total_income=total_income,
        total_expenses=total_expenses,
        remaining_budget=remaining_budget,
        budget_amount=budget_amount,
        budget_used=budget_used,
        savings=savings,
        recent_transactions=recent_transactions,
        category_totals=category_totals,
        monthly_income=income_series,
        monthly_expense=expense_series,
        months=history,
    )


@main_bp.route("/transactions")
def transactions():
    filters = {
        "type": request.args.get("type", "all"),
        "category": request.args.get("category", "all"),
        "month": request.args.get("month"),
        "search": request.args.get("search", ""),
        "start_date": request.args.get("start_date"),
        "end_date": request.args.get("end_date"),
    }
    transactions_list = get_transactions(filters)
    all_months = get_all_months()

    return render_template(
        "transactions.html",
        transactions=transactions_list,
        expense_categories=EXPENSE_CATEGORIES,
        income_categories=INCOME_CATEGORIES,
        all_months=all_months,
        selected_type=filters["type"] or "all",
        selected_category=filters["category"] or "all",
        selected_month=filters["month"] or "",
        search=filters["search"],
        start_date=filters["start_date"] or "",
        end_date=filters["end_date"] or "",
    )


@main_bp.route("/transactions/new", methods=["GET", "POST"])
def add_transaction_route():
    if request.method == "POST":
        amount = request.form.get("amount", type=float)
        txn_type = request.form.get("type")
        category = request.form.get("category")
        description = request.form.get("description", "").strip()
        date_value = request.form.get("date")

        if amount is None or amount <= 0:
            flash("Transaction amount must be greater than zero.", "error")
            return redirect(url_for("main.add_transaction_route"))
        if not txn_type or txn_type not in {"income", "expense"}:
            flash("Please select a valid transaction type.", "error")
            return redirect(url_for("main.add_transaction_route"))
        if not category:
            flash("Please select a category.", "error")
            return redirect(url_for("main.add_transaction_route"))
        if not date_value:
            flash("Please provide a transaction date.", "error")
            return redirect(url_for("main.add_transaction_route"))

        try:
            datetime.strptime(date_value, "%Y-%m-%d")
        except ValueError:
            flash("Invalid date format.", "error")
            return redirect(url_for("main.add_transaction_route"))

        add_transaction(amount, txn_type, category, date_value, description)
        flash("Transaction added successfully.", "success")
        return redirect(url_for("main.transactions"))

    return render_template(
        "transaction_form.html",
        transaction=None,
        expense_categories=EXPENSE_CATEGORIES,
        income_categories=INCOME_CATEGORIES,
        mode="add",
    )


@main_bp.route("/transactions/<int:transaction_id>/edit", methods=["GET", "POST"])
def edit_transaction_route(transaction_id):
    transaction = get_transaction_by_id(transaction_id)
    if not transaction:
        flash("Transaction not found.", "error")
        return redirect(url_for("main.transactions"))

    if request.method == "POST":
        amount = request.form.get("amount", type=float)
        txn_type = request.form.get("type")
        category = request.form.get("category")
        description = request.form.get("description", "").strip()
        date_value = request.form.get("date")

        if amount is None or amount <= 0:
            flash("Transaction amount must be greater than zero.", "error")
            return redirect(url_for("main.edit_transaction_route", transaction_id=transaction_id))
        if not txn_type or txn_type not in {"income", "expense"}:
            flash("Please select a valid transaction type.", "error")
            return redirect(url_for("main.edit_transaction_route", transaction_id=transaction_id))
        if not category:
            flash("Please select a category.", "error")
            return redirect(url_for("main.edit_transaction_route", transaction_id=transaction_id))

        try:
            datetime.strptime(date_value, "%Y-%m-%d")
        except ValueError:
            flash("Invalid date format.", "error")
            return redirect(url_for("main.edit_transaction_route", transaction_id=transaction_id))

        update_transaction(transaction_id, amount, txn_type, category, date_value, description)
        flash("Transaction updated successfully.", "success")
        return redirect(url_for("main.transactions"))

    return render_template(
        "transaction_form.html",
        transaction=transaction,
        expense_categories=EXPENSE_CATEGORIES,
        income_categories=INCOME_CATEGORIES,
        mode="edit",
    )


@main_bp.route("/transactions/<int:transaction_id>/delete", methods=["POST"])
def delete_transaction_route(transaction_id):
    if get_transaction_by_id(transaction_id) is None:
        flash("Transaction not found.", "error")
        return redirect(url_for("main.transactions"))

    delete_txn(transaction_id)
    flash("Transaction deleted successfully.", "success")
    return redirect(url_for("main.transactions"))


@main_bp.route("/budget", methods=["GET", "POST"])
def budget():
    current_month = datetime.today().strftime("%Y-%m")
    budget_record = get_budget_for_month(current_month)

    if request.method == "POST":
        amount = request.form.get("amount", type=float)
        if amount is None or amount < 0:
            flash("Budget amount must be zero or greater.", "error")
            return redirect(url_for("main.budget"))

        save_budget(current_month, amount)
        flash("Monthly budget saved successfully.", "success")
        return redirect(url_for("main.budget"))

    spent = sum(float(t["amount"]) for t in get_transactions({"type": "expense", "month": current_month}))
    configured_amount = float(budget_record["amount"]) if budget_record else 0.0
    remaining = configured_amount - spent
    percent_used = (spent / configured_amount * 100) if configured_amount else 0.0

    return render_template(
        "budget.html",
        budget_record=budget_record,
        spent=spent,
        remaining=remaining,
        percent_used=percent_used,
        configured_amount=configured_amount,
    )


@main_bp.route("/savings", methods=["GET", "POST"])
def savings():
    if request.method == "POST":
        form_action = request.form.get("action")
        if form_action == "create":
            name = request.form.get("name", "").strip()
            target_amount = request.form.get("target_amount", type=float)
            current_amount = request.form.get("current_amount", type=float)
            target_date = request.form.get("target_date")
            description = request.form.get("description", "").strip()

            if not name:
                flash("Goal name is required.", "error")
                return redirect(url_for("main.savings"))
            if target_amount is None or target_amount <= 0:
                flash("Target amount must be greater than zero.", "error")
                return redirect(url_for("main.savings"))
            if current_amount is None or current_amount < 0:
                flash("Current amount cannot be negative.", "error")
                return redirect(url_for("main.savings"))
            try:
                datetime.strptime(target_date, "%Y-%m-%d")
            except ValueError:
                flash("Invalid target date.", "error")
                return redirect(url_for("main.savings"))

            create_savings_goal(name, target_amount, current_amount, target_date, description)
            flash("Savings goal created successfully.", "success")
            return redirect(url_for("main.savings"))

        if form_action == "update":
            goal_id = request.form.get("goal_id", type=int)
            change_amount = request.form.get("change_amount", type=float)
            direction = request.form.get("direction")

            if change_amount is None or change_amount <= 0:
                flash("Amount change must be greater than zero.", "error")
                return redirect(url_for("main.savings"))

            updated = update_savings_goal(goal_id, change_amount, direction)
            if not updated:
                flash("Savings goal update failed due to invalid amount or goal.", "error")
                return redirect(url_for("main.savings"))

            flash("Savings goal updated successfully.", "success")
            return redirect(url_for("main.savings"))

    goals = get_savings_goals()
    return render_template("savings.html", goals=goals)


@main_bp.route("/statistics")
def statistics():
    month = request.args.get("month") or datetime.today().strftime("%Y-%m")
    monthly_summary = get_monthly_summary(month)
    monthly_income = float(monthly_summary.get("income", 0.0))
    monthly_expenses = float(monthly_summary.get("expense", 0.0))
    monthly_savings = monthly_income - monthly_expenses

    category_totals = get_monthly_expense_by_category(month)
    all_months = get_all_months()
    income_series = []
    expense_series = []
    for month_name in all_months:
        summary = get_monthly_summary(month_name)
        income_series.append(float(summary.get("income", 0.0)))
        expense_series.append(float(summary.get("expense", 0.0)))

    return render_template(
        "statistics.html",
        selected_month=month,
        months=all_months,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        monthly_savings=monthly_savings,
        category_totals=category_totals,
        income_series=income_series,
        expense_series=expense_series,
        chart_months=all_months,
    )
