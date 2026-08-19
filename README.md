# Finance Analytics Platform for Financial Reporting and Budget Tracking

## Project Overview

**FinSight** is a full-stack personal finance management and analytics platform built with Flask, SQLAlchemy, SQLite, and Chart.js. The platform enables users to track income, manage multi-category expenses, monitor bank and savings account balances, build budgets, manage investment portfolios, plan multi-step financial goals, link expenses directly with financial goals, receive automated event-driven financial alerts, and view interactive financial dashboards and reporting analytics.

All analytics, charts, alerts, and insights are generated dynamically from actual database-driven financial data.

---

## Key Features

### Financial Management
- **Secure User Authentication**: User registration, email format validation, password hashing (Flask-Bcrypt), session management, and route protection (Flask-Login).
- **Profile Management**: Personal user profile details and settings management.
- **Income Tracking**: Record, edit, delete, and categorize income streams.
- **Expense Tracking**: Log, edit, and delete category-specific expenses linked to accounts and financial goals.
- **Account Management & Balance Synchronization**: Manage bank and savings accounts with automatic balance synchronization upon adding, editing, or deleting expenses.
- **Budget Tracking**: Monthly budget allocation, spent vs. remaining budget calculations, usage percentage indicators, and budget status tracking (Healthy, Normal, Warning, Exceeded).
- **Financial Dashboard**: Unified overview with summary cards (Total Income, Total Expenses, Net Savings, Monthly Budget), category breakdown pie charts, expense trends, and recent transaction history.

### Financial Goals and Investments
- **Financial Goal Planning**: Create, edit, and track short-term and long-term financial goals with target amounts, current savings, target dates, priorities, and status indicators.
- **Goal Progress Tracking**: Automatic calculation of goal completion status, progress percentages, and remaining target amounts.
- **Multi-Step Goal Planning (Goal Parts)**: Deconstruct complex goals into ordered sub-steps/milestones with estimated costs, actual costs, cost variances, timelines, and completion statuses.
- **Investment Portfolio Tracking**: Track investments across instruments (Stocks, Mutual Funds, Fixed Deposits, Crypto, Gold).
- **Portfolio Value & Returns Tracking**: Automated calculations for Total Invested Amount, Current Portfolio Value, Total Returns (₹), Return Percentage (%), and Asset Allocation breakdown.

### Smart Analytics
- **Spending Pattern Analysis**: Category-wise expense distribution, top spending category detection, and total spending summaries.
- **Category-wise & Distribution Analysis**: Interactive doughnut and pie charts showing category breakdowns and goal-linked vs. regular expense distribution.
- **Monthly & Historical Spending Trends**: Multi-month historical Income vs. Expense vs. Net Savings trend line charts computed dynamically from transaction dates.
- **Weekly Spending Pattern**: Current month weekly spending breakdown across Weeks 1–5 with peak spending week identification.
- **Current vs. Previous Month Comparison**: MoM spending differences, percentage change, transaction counts, and category shifts.
- **Interactive Financial Charts**: Responsive Chart.js visualizations across all analytics views.
- **Expense-to-Goal Connection & Goal-Wise Analytics**: Direct mapping of expenses to financial goals with goal-linked expense summaries, totals, averages, and trend tracking.
- **Database-Driven Financial Insights**: Rule-based explainable insights detailing financial behavior, budget utilization, and savings rates based on real database records.

### Financial Alerts
- **Financial Event Alerts**: Automated event-driven alerts for Budget Warnings (80%), Budget Exceedances (100%), High Category Spending (>40%), Significant MoM Spending Increases (>15%), Negative Net Balances, Goal Milestones (25%, 50%, 75%, 100%), and Goal Deadlines.
- **Alert Dashboard (`/alerts`)**: Dedicated alert management page with summary metrics (Total, Unread, Critical, Read/Resolved) and filter options (All, Unread, Budget, Goal, Spending, Critical).
- **Mark Alerts as Read**: Interactive status toggle button to dismiss and manage alerts.
- **Alert Deduplication**: Guarantees zero alert duplication on page refreshes and user actions.

---

## Expense-to-Goal Connection

Expenses can optionally be associated with financial goals. This relationship allows the platform to track goal-related spending dynamically, integrating expense data directly into goal details and financial analytics.

- **Optional Goal Linking**: An expense can optionally be linked to a goal (`goal_id`), remain unlinked (`NULL`), or belong to a budget.
- **One-to-Many Relationship**: A single Goal can have multiple associated Expenses.
- **Database Persistence**: Stored via the nullable `goal_id` foreign key on the `expenses` table referencing `goals.id`.
- **Goal Details Integration**: Goal detail views dynamically retrieve and display direct goal-linked expenses, total goal-related spending, and expense counts.
- **Goal-Wise Analytics**: Analytics engine computes:
  - Goal-linked expenses vs. regular non-goal expenses
  - Total spending associated with each goal
  - Number of linked expenses and average expense amounts
  - Monthly goal-linked expense trend visualization

---

## Technology Stack

| Category | Technologies |
| :--- | :--- |
| **Backend** | Python 3, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt, SQLAlchemy |
| **Database** | SQLite |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Jinja2 Templating, Chart.js, FontAwesome |
| **Architecture** | Modular Flask Blueprints, Decoupled Service Layer, Model-View-Controller (MVC) Pattern |

---

## Project Structure

```
Smart-Finance-Insights/
├── app.py                      # Application entry point & main controllers
├── config.py                   # Configuration settings & database configuration
├── extensions.py               # Extension initializations (DB, LoginManager, Bcrypt)
├── requirements.txt            # Project dependencies
├── database/                   # SQLite database directory
│   └── finance.db
├── models/                     # SQLAlchemy database models
│   ├── user.py
│   ├── profile.py
│   ├── account.py
│   ├── income.py
│   ├── expense.py              # Expense model with Account and Goal relationships
│   ├── budget.py               # Budget model with Goal relationship
│   ├── goal.py                 # Goal model with Expense and Budget relationships
│   ├── goal_part.py
│   ├── investment.py
│   └── alert.py
├── routes/                     # Blueprint routes
│   ├── auth.py
│   ├── profile.py
│   ├── account.py
│   ├── income.py
│   ├── expense.py
│   ├── budget.py
│   ├── goal.py
│   ├── investment.py
│   ├── analytics.py
│   └── alert.py
├── services/                   # Business logic and analytics engines
│   ├── spending_analysis.py    # Spending analytics, trends & goal-expense calculations
│   └── alert_service.py        # Event alert detection & deduplication engine
├── static/                     # Static assets
│   ├── css/
│   └── js/
└── templates/                  # Jinja2 HTML templates
    ├── layout.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── analytics.html
    ├── alerts.html
    ├── expenses.html
    ├── edit_expense.html
    ├── income.html
    ├── budgets.html
    ├── goals.html
    ├── goal_details.html
    ├── investments.html
    ├── accounts.html
    └── profile.html
```

---

## Key Database Relationships

```
User
├── Income
├── Expenses
├── Accounts
├── Budgets
├── Goals
├── Investments
└── Alerts

Expense
├── Account (Required)
└── Goal (Optional)

Budget
└── Goal (Optional)

Goal
├── Goal Parts
├── Expenses (Optional)
└── Budgets (Optional)
```

---

## Security and Data Management

- **Password Hashing**: Passwords are securely hashed using bcrypt prior to database storage.
- **Authentication & Session Security**: Route access is protected using `@login_required` decorators with session management via Flask-Login.
- **Strict Data Isolation**: Database queries and analytics engines filter records strictly by `current_user.id` to enforce user-level data privacy.

---

## Screenshots

- **Dashboard**: High-level financial cards, income/expense summaries, account balances, and recent transactions.
- **Expense Management**: Categorized expense entry, account balance sync, and optional goal linking dropdown.
- **Financial Goals**: Goal progress bars, milestone step breakdowns, and goal-linked expense tables.
- **Financial Analytics**: Multi-tab analytics featuring spending patterns, monthly trends, budget status, and goal-wise expense charts.
- **Alert Dashboard**: Event alert list with severity indicators, filtering, and mark-as-read controls.

---

## How to Run

### 1. Clone the repository
```bash
git clone https://github.com/M-Raghavendra/Smart-Finance-Insights.git
cd Smart-Finance-Insights
```

### 2. Create a virtual environment
```bash
python -m venv .venv
```

### 3. Activate the virtual environment
- **Windows**:
  ```cmd
  .venv\Scripts\activate
  ```
- **macOS / Linux**:
  ```bash
  source .venv/bin/activate
  ```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the application
```bash
python app.py
```

Open your browser and navigate to `http://127.0.0.1:5000` to use the application.
