
# Finance Tracker

### A simple personal finance dashboard for understanding where your money goes.

Finance Tracker is a local-first personal finance web application for recording income and expenses, managing budgets, tracking savings goals, and understanding spending patterns over time.

It combines a straightforward transaction ledger with budgeting and analytics features so that financial activity can be recorded and reviewed from one place.

---

## What Problem Does It Solve?

Tracking money manually can quickly become messy.

Transactions end up scattered across notes, banking apps, spreadsheets, and memory. Even when the numbers are available, it can be difficult to answer simple questions like:

- How much did I spend this month?
- Where is most of my money going?
- How much of my budget is left?
- How much have I saved toward a goal?
- How does this month compare with previous months?
- How much can I reasonably spend per day?

Finance Tracker brings these questions into one dashboard.

---

## Features

### Transaction Management

Record and manage financial transactions with:

- Income and expense types
- Amount
- Category
- Date
- Description
- Edit and delete functionality
- Transaction history
- Search
- Category filtering
- Income/expense filtering
- Month filtering
- Custom date-range filtering

Transactions are persisted locally using SQLite.

### Dashboard

The dashboard provides an overview of the current financial picture, including:

- Current-month income
- Current-month expenses
- Remaining budget
- Budget utilization
- Savings progress
- Recent transactions
- Spending by category
- Monthly income history
- Monthly expense history
- Smart daily budget

This makes the dashboard the main starting point for reviewing financial activity.

### Budget Management

Create monthly budgets and monitor how much has been spent against the configured amount.

The application calculates:

```text
Remaining Budget = Budget - Expenses
````

and:

```
Budget Used (%) = Expenses / Budget × 100
```

Budget items can also be added and removed from the budget view.

### Savings Goals

Create savings goals with:

- Goal name
- Target amount
- Current amount
- Target date
- Description

Savings progress can then be updated as money is added toward the goal.

### Spending Analytics

Finance Tracker groups expenses by category and provides monthly income/expense summaries.

Supported expense categories include:

- Food
- Transport
- Education
- Bills
- Entertainment
- Shopping
- Health
- Other

Income can be categorized as:

- Allowance
- Salary
- Freelance
- Gift
- Other

### Multiple Local Accounts

The application supports separate local account data contexts.

An active account is selected through a cookie, and transactions, budgets, and savings data are associated with that account.

### Smart Daily Budget

Finance Tracker calculates a daily spending allowance based on the current month's budget and spending state.

The goal is to turn a monthly budget into a more practical day-to-day spending guideline.

---

## Architecture

```
                    ┌─────────────────────┐
                    │     Web Browser     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       Flask         │
                    │   Web Application   │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
       ┌──────────────────┐       ┌──────────────────┐
       │   Route Layer    │       │  HTML Templates  │
       │                  │       │                  │
       │ Transactions     │       │ Dashboard        │
       │ Budget           │       │ Transactions     │
       │ Savings          │       │ Budget           │
       │ Dashboard        │       │ Savings          │
       └────────┬─────────┘       └──────────────────┘
                │
                ▼
       ┌──────────────────┐
       │   Data Access    │
       │                  │
       │ Transactions     │
       │ Budgets          │
       │ Savings Goals    │
       │ Analytics        │
       └────────┬─────────┘
                │
                ▼
       ┌──────────────────┐
       │      SQLite      │
       │                  │
       │ Local persistence│
       └──────────────────┘
```

The application separates routing, data-access logic, database handling, models, security helpers, and presentation templates.

---

## Technology Stack

|Layer|Technology|
|---|---|
|Backend|Python|
|Web Framework|Flask|
|Database|SQLite|
|Frontend|HTML / CSS / JavaScript|
|Templates|Jinja2|
|Server|Flask development server / Gunicorn|
|Testing|Python test suite|

The current dependency file specifies Flask 3.1.1 and Gunicorn.

---

## Project Structure

```
finance-tracker/
│
├── finance_tracker/
│   ├── routes/
│   │   ├── __init__.py
│   │   └── main.py
│   │
│   ├── data_access.py
│   ├── database.py
│   ├── helpers.py
│   ├── models.py
│   └── security.py
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── dashboard.html
│   ├── transactions.html
│   ├── transaction_form.html
│   ├── budget.html
│   ├── savings.html
│   └── statistics.html
│
├── static/
├── tests/
├── app.py
├── main.py
├── config.py
├── requirements.txt
└── README.md
```

---

## Data Model

The application revolves around three main financial entities:

### Transactions

```
Transaction
├── id
├── account_id
├── amount
├── type
├── category
├── date
├── description
└── created_at
```

### Budgets

```
Budget
├── id
├── account_id
├── month
├── amount
├── created_at
└── updated_at
```

### Savings Goals

```
Savings Goal
├── id
├── account_id
├── name
├── target_amount
├── current_amount
├── target_date
├── description
└── created_at
```

These models form the foundation for the application's transaction management, budgeting, savings, and analytics workflows.

---

## Getting Started

### Requirements

- Python 3.10+
- pip

### 1. Clone the repository

```
git clone https://github.com/SamInvader/finance-tracker.git
cd finance-tracker
```

### 2. Create a virtual environment

#### Windows

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### macOS / Linux

```
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Start the application

```
python app.py
```

The application runs locally at:

```
http://127.0.0.1:5000
```

The application's entry point starts Flask on localhost port 5000.

---

## How It Works

A typical workflow looks like this:

```
Add income / expense
        ↓
Transaction stored in SQLite
        ↓
Dashboard recalculates totals
        ↓
Expenses grouped by category
        ↓
Budget usage updated
        ↓
Monthly statistics updated
        ↓
Smart daily budget recalculated
```

This keeps the application simple while allowing the same underlying transaction data to power multiple parts of the interface.

---

## Design Goals

### Simple over complicated

Finance Tracker is intentionally built around a small number of core concepts rather than trying to become a full banking platform.

### Local data

The application uses a local SQLite database instead of requiring a remote database service for its core functionality.

### Useful calculations

The application focuses on turning raw transactions into information that is easier to act on:

- Spending totals
- Budget remaining
- Budget utilization
- Category breakdowns
- Monthly trends
- Savings progress
- Daily spending guidance

### Clear separation of concerns

Routing, persistence, models, templates, and helper functions are separated into different parts of the project so the application can evolve without putting everything into a single file.

---

## Testing

Tests are included in the repository under:

```
tests/
```

Run the test suite with:

```
pytest
```

---

## Current Scope

Finance Tracker currently focuses on:

- Manual transaction tracking
- Personal budgeting
- Savings goals
- Spending analysis
- Local persistence
- Multiple local account contexts

It does **not** connect directly to bank accounts or automatically import transactions from financial institutions.

---

## Future Improvements

Possible future directions include:

- Better financial visualizations
    
- Recurring transactions
    
- Export to CSV
    
- Import from CSV
    
- More advanced budget categories
    
- Recurring budget planning
    
- Improved authentication
    
- Responsive mobile improvements
    
- API endpoints for external clients
    
- More comprehensive automated testing
    
- Deployment configuration
    

---

## Project Status

**Active development**

Finance Tracker is a personal finance management project focused on building a practical understanding of financial data, persistence, analytics, and full-stack web application structure.


## License

See the repository for license information.
