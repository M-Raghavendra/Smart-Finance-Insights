import os
import sys

# Ensure project root is in python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
from datetime import date
from app import app as flask_app
from extensions import db, bcrypt
from models.user import User
from models.profile import Profile
from models.expense import Expense
from models.income import Income
from models.budget import Budget
from models.goal import Goal
from models.goal_part import GoalPart
from models.account import Account
from models.investment import Investment
from models.alert import FinancialAlert
from services.report_service import get_monthly_financial_report, get_goal_progress_report
from services.spending_analysis import calculate_financial_health_score, get_spending_analysis
from services.alert_service import check_and_create_alerts


@pytest.fixture
def client():
    """
    Test fixture providing a clean Flask test client with test user isolation.
    """
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['RATELIMIT_ENABLED'] = False
    from extensions import limiter
    limiter.reset()

    test_emails = [
        "alice@example.com", "usera@example.com", "userb@example.com",
        "report@example.com", "goaluser@example.com", "export@example.com",
        "val@example.com", "empty@example.com", "m3@example.com",
        "val2@example.com", "drawer@example.com", "test@example.com",
        "theme_user@example.com"
    ]

    with flask_app.app_context():
        db.create_all()
        test_users = User.query.filter(User.email.in_(test_emails)).all()
        for u in test_users:
            Expense.query.filter_by(user_id=u.id).delete()
            Income.query.filter_by(user_id=u.id).delete()
            Budget.query.filter_by(user_id=u.id).delete()
            v_goals = Goal.query.filter_by(user_id=u.id).all()
            for g in v_goals:
                GoalPart.query.filter_by(goal_id=g.id).delete()
            Goal.query.filter_by(user_id=u.id).delete()
            Account.query.filter_by(user_id=u.id).delete()
            Investment.query.filter_by(user_id=u.id).delete()
            FinancialAlert.query.filter_by(user_id=u.id).delete()
            Profile.query.filter_by(user_id=u.id).delete()
            db.session.delete(u)
        db.session.commit()

    with flask_app.test_client() as test_client:
        yield test_client
        with flask_app.app_context():
            db.session.remove()


def register_and_login(client, name="Test User", email="test@example.com", password="Password123!"):
    """Helper function to register and log in a test user."""
    client.post("/register", data={
        "full_name": name,
        "email": email,
        "password": password
    })
    return client.post("/login", data={
        "email": email,
        "password": password
    }, follow_redirects=True)


# ==============================================================================
# 1. AUTHENTICATION & SECURITY TESTS
# ==============================================================================

def test_auth_registration_and_login(client):
    """Verifies password hashing, user registration, login, and invalid password handling."""
    res = client.post("/register", data={
        "full_name": "Alice Developer",
        "email": "alice@example.com",
        "password": "SecurePassword123!"
    })
    assert res.status_code in (200, 302)

    with flask_app.app_context():
        user = User.query.filter_by(email="alice@example.com").first()
        assert user is not None
        assert user.password != "SecurePassword123!"  # Password must be hashed
        assert bcrypt.check_password_hash(user.password, "SecurePassword123!")

    # Invalid password login
    res_bad = client.post("/login", data={
        "email": "alice@example.com",
        "password": "WrongPassword"
    })
    assert res_bad.status_code in (401, 400, 200)

    # Valid login
    res_ok = client.post("/login", data={
        "email": "alice@example.com",
        "password": "SecurePassword123!"
    }, follow_redirects=True)
    assert res_ok.status_code == 200


def test_route_protection(client):
    """Verifies unauthenticated users are redirected to login for protected routes."""
    protected_routes = [
        "/dashboard", "/expenses", "/income", "/budgets",
        "/goals", "/investments", "/analytics", "/alerts",
        "/reports", "/accounts", "/profile"
    ]
    for route in protected_routes:
        res = client.get(route, follow_redirects=False)
        assert res.status_code == 302
        assert "/login" in res.location


def test_user_data_isolation(client):
    """Verifies User A cannot access User B's financial data or reports."""
    # Register & setup User A
    register_and_login(client, name="User A", email="usera@example.com")
    with flask_app.app_context():
        user_a = User.query.filter_by(email="usera@example.com").first()
        acc_a = Account(account_name="User A Bank", account_type="Savings", balance=1000.0, user_id=user_a.id)
        db.session.add(acc_a)
        db.session.commit()
        exp_a = Expense(title="User A Secret Expense", category="Shopping", amount=250.0, payment_method="Debit Card", account_id=acc_a.id, expense_date=date.today(), user_id=user_a.id)
        db.session.add(exp_a)
        db.session.commit()
        exp_a_id = exp_a.id

    client.get("/logout")

    # Register & log in User B
    register_and_login(client, name="User B", email="userb@example.com")

    # User B tries to view or delete User A's expense
    res_del = client.get(f"/expense/delete/{exp_a_id}")
    assert res_del.status_code == 404

    # User B views reports page; must show 0 expenses
    with flask_app.app_context():
        user_b = User.query.filter_by(email="userb@example.com").first()
        report_b = get_monthly_financial_report(user_b.id)
        assert report_b['total_expenses'] == 0.0


# ==============================================================================
# 2. MILESTONE 4 FINANCIAL REPORTS & EXPORTS TESTS
# ==============================================================================

def test_monthly_financial_report_calculation(client):
    """Tests dynamic monthly report aggregation for income, expenses, savings, and budget."""
    register_and_login(client, name="Report User", email="report@example.com")

    with flask_app.app_context():
        u = User.query.filter_by(email="report@example.com").first()
        acc = Account(account_name="Main Acc", account_type="Checking", balance=5000.0, user_id=u.id)
        db.session.add(acc)
        db.session.commit()

        inc = Income(title="Salary", source="Job", amount=4000.0, income_date=date(2026, 8, 10), user_id=u.id)
        exp1 = Expense(title="Groceries", category="Food & Dining", amount=500.0, payment_method="Cash", account_id=acc.id, expense_date=date(2026, 8, 15), user_id=u.id)
        exp2 = Expense(title="Rent", category="Housing", amount=1500.0, payment_method="Bank Transfer", account_id=acc.id, expense_date=date(2026, 8, 1), user_id=u.id)
        bgt = Budget(monthly_budget=3000.0, month="August", year=2026, user_id=u.id)

        db.session.add_all([inc, exp1, exp2, bgt])
        db.session.commit()

        rpt = get_monthly_financial_report(u.id, month_input=8, year_input=2026)
        assert rpt['total_income'] == 4000.0
        assert rpt['total_expenses'] == 2000.0
        assert rpt['net_savings'] == 2000.0
        assert rpt['budget_utilization'] == round((2000.0 / 3000.0) * 100, 1)


def test_goal_progress_report(client):
    """Tests goal progress report and linked expense calculations."""
    register_and_login(client, name="Goal User", email="goaluser@example.com")

    with flask_app.app_context():
        u = User.query.filter_by(email="goaluser@example.com").first()
        g = Goal(goal_name="Emergency Fund", goal_type="Savings", target_amount=10000.0, current_amount=4000.0, target_date=date(2026, 12, 31), category="Savings", user_id=u.id)
        db.session.add(g)
        db.session.commit()

        acc = Account(account_name="Goal Acc", account_type="Savings", balance=4000.0, user_id=u.id)
        db.session.add(acc)
        db.session.commit()

        e = Expense(title="Goal Deposit", category="Savings", amount=1000.0, payment_method="Transfer", account_id=acc.id, expense_date=date.today(), goal_id=g.id, user_id=u.id)
        db.session.add(e)
        db.session.commit()

        grpt = get_goal_progress_report(u.id)
        assert grpt['total_goals_count'] == 1
        assert grpt['goals'][0]['progress_percentage'] == 40.0
        assert grpt['goals'][0]['remaining_amount'] == 6000.0
        assert grpt['goals'][0]['linked_expenses_count'] == 1


def test_report_export_endpoints(client):
    """Tests PDF, Word, and Excel export endpoints."""
    register_and_login(client, name="Export User", email="export@example.com")

    # Test PDF Export
    res_pdf = client.get("/reports/export/pdf?month=8&year=2026")
    assert res_pdf.status_code == 200
    assert res_pdf.mimetype == "application/pdf"
    assert len(res_pdf.data) > 0

    # Test Word Export
    res_docx = client.get("/reports/export/docx?month=8&year=2026")
    assert res_docx.status_code == 200
    assert "wordprocessingml" in res_docx.mimetype
    assert len(res_docx.data) > 0

    # Test Excel Export
    res_xlsx = client.get("/reports/export/excel?month=8&year=2026")
    assert res_xlsx.status_code == 200
    assert "spreadsheetml" in res_xlsx.mimetype
    assert len(res_xlsx.data) > 0


# ==============================================================================
# 3. INPUT VALIDATION & EMPTY DATA HANDLING TESTS
# ==============================================================================

def test_input_validation(client):
    """Tests server-side handling of invalid amounts and malformed dates."""
    register_and_login(client, name="Validation User", email="val@example.com")

    # Negative amount expense submit
    res_neg = client.post("/expenses", data={
        "title": "Invalid Expense",
        "category": "Food",
        "amount": "-50.0",
        "payment_method": "Cash",
        "account_id": "1",
        "expense_date": "2026-08-15"
    }, follow_redirects=True)
    assert res_neg.status_code == 200
    assert b"greater than zero" in res_neg.data

    # Malformed date expense submit
    res_date = client.post("/expenses", data={
        "title": "Bad Date",
        "category": "Food",
        "amount": "50.0",
        "payment_method": "Cash",
        "account_id": "1",
        "expense_date": "invalid-date"
    }, follow_redirects=True)
    assert res_date.status_code == 200
    assert b"Invalid expense date format" in res_date.data


def test_empty_data_handling(client):
    """Ensures application routes and reports do not crash when user has 0 records."""
    register_and_login(client, name="Empty User", email="empty@example.com")

    with flask_app.app_context():
        u = User.query.filter_by(email="empty@example.com").first()
        rpt = get_monthly_financial_report(u.id)
        assert rpt['total_income'] == 0.0
        assert rpt['total_expenses'] == 0.0
        assert rpt['budget_utilization'] == 0.0

        health = calculate_financial_health_score(u.id)
        assert health['score'] >= 0

    res = client.get("/reports")
    assert res.status_code == 200
    assert b"No expense entries recorded" in res.data


# ==============================================================================
# 4. MILESTONE 3 REGRESSION TESTS
# ==============================================================================

def test_milestone3_regression(client):
    """Verifies Milestone 3 Financial Health Score, spending analysis, and alerts."""
    register_and_login(client, name="M3 User", email="m3@example.com")

    with flask_app.app_context():
        u = User.query.filter_by(email="m3@example.com").first()
        acc = Account(account_name="M3 Acc", account_type="Savings", balance=1000.0, user_id=u.id)
        db.session.add(acc)
        db.session.commit()

        bgt = Budget(monthly_budget=500.0, month="August", year=2026, user_id=u.id)
        exp = Expense(title="Overbudget Item", category="Shopping", amount=600.0, payment_method="Card", account_id=acc.id, expense_date=date.today(), user_id=u.id)
        db.session.add_all([bgt, exp])
        db.session.commit()

        # Check alerts generation
        alerts = check_and_create_alerts(u.id)
        assert len(alerts) > 0
        assert any(a.title == "Budget Exceeded" for a in alerts)

        # Check health score
        health = calculate_financial_health_score(u.id)
        assert health['score'] < 100  # Overbudget penalty applied


# ==============================================================================
# 5. NEW MILESTONE 4 ENHANCEMENT TESTS
# ==============================================================================

def test_budget_and_account_input_validation(client):
    """Verifies server-side validation for invalid/negative budget and account inputs."""
    register_and_login(client, name="Validation User 2", email="val2@example.com")

    # Negative budget submit
    res_bgt_neg = client.post("/budgets", data={
        "monthly_budget": "-500",
        "month": "August",
        "year": "2026"
    }, follow_redirects=True)
    assert res_bgt_neg.status_code == 200
    assert b"must be greater than zero" in res_bgt_neg.data

    # Malformed budget submit
    res_bgt_str = client.post("/budgets", data={
        "monthly_budget": "abc",
        "month": "August",
        "year": "2026"
    }, follow_redirects=True)
    assert res_bgt_str.status_code == 200
    assert b"Invalid monthly budget amount format" in res_bgt_str.data

    # Malformed account balance submit
    res_acc_str = client.post("/accounts", data={
        "account_name": "Invalid Acc",
        "account_type": "Checking",
        "balance": "invalid_num"
    }, follow_redirects=True)
    assert res_acc_str.status_code == 200
    assert b"Invalid account balance format" in res_acc_str.data


def test_alert_date_filtering_and_ui_drawer(client):
    """Verifies alert date range filtering and presence of right-side notification popup drawer."""
    register_and_login(client, name="Drawer User", email="drawer@example.com")

    with flask_app.app_context():
        u = User.query.filter_by(email="drawer@example.com").first()
        a1 = FinancialAlert(user_id=u.id, alert_type="budget_warning", title="Test Alert", message="Msg", severity="warning", is_read=False)
        db.session.add(a1)
        db.session.commit()

    # Check notification bell & drawer presence on dashboard
    res_dash = client.get("/dashboard")
    assert res_dash.status_code == 200
    assert b"notificationBellBtn" in res_dash.data
    assert b"notificationDrawer" in res_dash.data

    # Check date range filtering on /alerts
    today_str = date.today().strftime("%Y-%m-%d")
    res_filter = client.get(f"/alerts?from_date={today_str}&to_date={today_str}")
    assert res_filter.status_code == 200
    assert b"Test Alert" in res_filter.data


def test_theme_system(client):
    """Verifies 2-theme system (Light & Dark only), removal of System Default, global header dropdown placement, and DB persistence."""
    register_and_login(client, name="Theme User", email="theme_user@example.com")

    with flask_app.app_context():
        u = User.query.filter_by(email="theme_user@example.com").first()
        assert u is not None
        assert u.theme_preference == "light"  # Default theme for new user is Light

    # 1. Verify global top header renders compact theme control dropdown left of notification bell
    res_dash = client.get("/dashboard")
    assert res_dash.status_code == 200
    assert b"nav-theme-dropdown" in res_dash.data
    assert b"themeDropdownBtn" in res_dash.data
    assert b"notificationBellBtn" in res_dash.data
    assert b"System Default" not in res_dash.data  # System Default option removed

    # 2. Verify Profile page does NOT contain Theme Preference selector
    res_prof_view = client.get("/profile")
    assert res_prof_view.status_code == 200
    assert b"theme-selector-container" not in res_prof_view.data

    # 3. Change theme to 'dark' via instant endpoint
    res_dark = client.post("/profile/theme", json={"theme_preference": "dark"})
    assert res_dark.status_code == 200
    assert res_dark.json["status"] == "success"

    with flask_app.app_context():
        u = User.query.filter_by(email="theme_user@example.com").first()
        assert u.theme_preference == "dark"

    # 4. Change theme to 'light'
    res_light = client.post("/profile/theme", json={"theme_preference": "light"})
    assert res_light.status_code == 200

    with flask_app.app_context():
        u = User.query.filter_by(email="theme_user@example.com").first()
        assert u.theme_preference == "light"

    # 5. Invalid selection 'system' should be rejected
    res_sys = client.post("/profile/theme", json={"theme_preference": "system"})
    assert res_sys.status_code == 400


def test_csrf_token_protection():
    """Verifies explicit CSRF token protection: rejects missing/invalid tokens and accepts valid tokens."""
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = True

    with flask_app.test_client() as csrf_client:
        # 1. Missing CSRF token -> HTTP 400
        res_missing = csrf_client.post("/login", data={"email": "alice@example.com", "password": "Password123!"})
        assert res_missing.status_code == 400
        assert b"CSRF" in res_missing.data

        # 2. Invalid CSRF token -> HTTP 400
        res_invalid = csrf_client.post("/login", data={"email": "alice@example.com", "password": "Password123!", "csrf_token": "invalid_token_123"})
        assert res_invalid.status_code == 400
        assert b"CSRF" in res_invalid.data

        # 3. Valid CSRF token extracted from HTML form -> succeeds beyond CSRF validation
        res_get = csrf_client.get("/login")
        assert res_get.status_code == 200
        import re
        match = re.search(r'name="csrf_token" value="([^"]+)"', res_get.data.decode("utf-8"))
        assert match is not None
        valid_csrf_token = match.group(1)

        res_valid = csrf_client.post("/login", data={
            "email": "alice@example.com",
            "password": "Password123!",
            "csrf_token": valid_csrf_token
        })
        assert res_valid.status_code != 400  # Passed CSRF check

    # Restore default test configuration
    flask_app.config['WTF_CSRF_ENABLED'] = False


def test_login_rate_limiting():
    """Verifies login rate limiting: allows 5 attempts per minute, 6th attempt returns HTTP 429."""
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['RATELIMIT_ENABLED'] = True

    from extensions import limiter
    limiter.reset()

    with flask_app.test_client() as rl_client:
        # First 5 attempts return normal auth errors (404/401)
        for _ in range(5):
            res = rl_client.post("/login", data={"email": "nonexistent_ratelimit@example.com", "password": "BadPassword123!"})
            assert res.status_code in (404, 401, 400)

        # 6th attempt exceeds rate limit -> HTTP 429
        res_limit = rl_client.post("/login", data={"email": "nonexistent_ratelimit@example.com", "password": "BadPassword123!"})
        assert res_limit.status_code == 429
        assert b"Too many login attempts" in res_limit.data

    limiter.reset()
    flask_app.config['RATELIMIT_ENABLED'] = False


