import os
import sys
from datetime import date, datetime, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.insert(0, PROJECT_ROOT)

from app import app, init_db_schema
from extensions import db, bcrypt
from models import User, Expense, Income, Budget, Goal, GoalPart, Investment, Account, FinancialAlert
from services.spending_analysis import get_spending_analysis, get_monthly_spending_trend, get_goal_expense_analytics
from services.alert_service import check_and_create_alerts, get_user_alerts

def setup_exact_presentation_data():
    print("============================================================")
    print("SETTING UP EXACT PRESENTATION DATASET (VICKY)")
    print("============================================================")

    with app.app_context():
        init_db_schema()

        # 1. User check & credentials update
        vicky_email = "vicky@gmail.com"
        user = User.query.filter_by(email=vicky_email).first()
        if not user:
            pw_hash = bcrypt.generate_password_hash("Vicky@123").decode("utf-8")
            user = User(full_name="Vicky", email=vicky_email, password=pw_hash)
            db.session.add(user)
            db.session.commit()
        else:
            # Ensure password hash is updated to Vicky@123
            user.password = bcrypt.generate_password_hash("Vicky@123").decode("utf-8")
            user.full_name = "Vicky"
            db.session.commit()
        
        uid = user.id
        print(f"Target User: {user.full_name} ({user.email}) [ID: {uid}]")

        # 2. Clear old records for Vicky cleanly
        old_budgets = Budget.query.filter_by(user_id=uid).all()
        for b in old_budgets:
            b.goal_id = None
        db.session.commit()

        FinancialAlert.query.filter_by(user_id=uid).delete()
        if Goal.query.filter_by(user_id=uid).count() > 0:
            goal_ids = [g.id for g in Goal.query.filter_by(user_id=uid).all()]
            GoalPart.query.filter(GoalPart.goal_id.in_(goal_ids)).delete(synchronize_session=False)
        Expense.query.filter_by(user_id=uid).delete()
        Income.query.filter_by(user_id=uid).delete()
        Budget.query.filter_by(user_id=uid).delete()
        Investment.query.filter_by(user_id=uid).delete()
        Goal.query.filter_by(user_id=uid).delete()
        Account.query.filter_by(user_id=uid).delete()
        db.session.commit()
        print("  - Purged old records for Vicky.")

        # 3. Primary Account
        # Initial Opening Balance: ₹10,000
        # Income added: +₹30,000
        # Expenses deducted: -₹22,750
        # Final Account Balance = ₹17,250
        account = Account(
            account_name="Primary Bank Account",
            account_type="Savings",
            balance=17250.0,
            description="Primary bank account for stipend, salary and daily expenses",
            user_id=uid
        )
        db.session.add(account)
        db.session.commit()
        print(f"  - Created Primary Bank Account (Final Balance: ₹{account.balance:,.2f}).")

        # 4. Income Record (Total = ₹30,000)
        salary_income = Income(
            title="Monthly Stipend & Salary",
            source="Salary",
            amount=30000.0,
            income_date=date(2026, 8, 1),
            description="Monthly income from salary and stipend",
            user_id=uid
        )
        db.session.add(salary_income)
        db.session.commit()
        print("  - Created Income record (Total Income = ₹30,000.00).")

        # 5. Financial Goals (3 realistic goals)
        # Goal 1: Higher Education Fund (Target: ₹50,000, Saved: ₹25,000, Deadline approaching in 25 days)
        # Goal 2: Laptop Purchase (Target: ₹40,000, Saved: ₹20,000, Target: Dec 31, 2026)
        # Goal 3: Emergency Fund (Target: ₹30,000, Saved: ₹15,000, Target: June 30, 2027)
        deadline_date = date.today() + timedelta(days=25)
        goals_data = [
            {
                "name": "Higher Education Fund",
                "type": "Long Term",
                "target": 50000.0,
                "current": 25000.0,
                "date": deadline_date,
                "category": "Education",
                "priority": "High",
                "notes": "Fund for advanced certifications and higher education"
            },
            {
                "name": "Laptop Purchase",
                "type": "Short Term",
                "target": 40000.0,
                "current": 20000.0,
                "date": date(2026, 12, 31),
                "category": "Shopping",
                "priority": "Medium",
                "notes": "Goal for upgrading development laptop"
            },
            {
                "name": "Emergency Fund",
                "type": "Long Term",
                "target": 30000.0,
                "current": 15000.0,
                "date": date(2027, 6, 30),
                "category": "Savings",
                "priority": "High",
                "notes": "Safety net for unexpected expenses"
            }
        ]

        created_goals = []
        for g in goals_data:
            g_obj = Goal(
                goal_name=g["name"],
                goal_type=g["type"],
                target_amount=g["target"],
                current_amount=g["current"],
                target_date=g["date"],
                category=g["category"],
                priority=g["priority"],
                status="In Progress",
                notes=g["notes"],
                user_id=uid
            )
            db.session.add(g_obj)
            created_goals.append(g_obj)
        db.session.commit()
        print(f"  - Created {len(created_goals)} financial goals.")

        education_goal = created_goals[0]
        laptop_goal = created_goals[1]

        # Add Goal Parts for realism
        gp1 = GoalPart(
            goal_id=education_goal.id,
            part_name="Course Registration & Fees",
            step_order=1,
            description="Initial admission & course registration fee",
            estimated_cost=15000.0,
            actual_cost=15000.0,
            start_date=date(2026, 1, 10),
            completion_date=date(2026, 6, 15),
            status="Completed",
            notes="Paid during initial registration"
        )
        gp2 = GoalPart(
            goal_id=laptop_goal.id,
            part_name="Laptop Down Payment",
            step_order=1,
            description="Initial down payment for laptop",
            estimated_cost=15000.0,
            actual_cost=15000.0,
            start_date=date(2026, 2, 1),
            completion_date=date(2026, 7, 1),
            status="Completed",
            notes="First installment phase"
        )
        db.session.add_all([gp1, gp2])
        db.session.commit()

        # 6. Expenses (7 realistic records, Total = ₹22,750)
        # Categories:
        # Food: ₹6,000 (Groceries ₹4,000 + Dining ₹2,000)
        # Education: ₹5,000 (Semester Tuition Fee linked to Higher Education Fund)
        # Shopping: ₹4,000 (Laptop Accessories & Books linked to Laptop Purchase)
        # Transport: ₹3,000 (Metro Pass & Fuel)
        # Utilities: ₹2,500 (Electricity & Internet Bill)
        # Entertainment: ₹2,250 (Movies & Streaming Subscriptions)
        expenses_data = [
            {
                "title": "Semester Tuition Fee",
                "category": "Education",
                "amount": 5000.0,
                "payment_method": "Net Banking",
                "date": date(2026, 8, 5),
                "desc": "Tuition fee for higher education program",
                "goal_id": education_goal.id
            },
            {
                "title": "Monthly Groceries",
                "category": "Food",
                "amount": 4000.0,
                "payment_method": "UPI",
                "date": date(2026, 8, 3),
                "desc": "Supermarket monthly grocery shopping",
                "goal_id": None
            },
            {
                "title": "Dining & Cafeteria",
                "category": "Food",
                "amount": 2000.0,
                "payment_method": "Card",
                "date": date(2026, 8, 14),
                "desc": "Weekend dining & snacks",
                "goal_id": None
            },
            {
                "title": "Laptop Accessories & Books",
                "category": "Shopping",
                "amount": 4000.0,
                "payment_method": "Credit Card",
                "date": date(2026, 8, 10),
                "desc": "External monitor & reference books",
                "goal_id": laptop_goal.id
            },
            {
                "title": "Monthly Metro Pass & Fuel",
                "category": "Transport",
                "amount": 3000.0,
                "payment_method": "UPI",
                "date": date(2026, 8, 8),
                "desc": "Commute travel card recharge & petrol",
                "goal_id": None
            },
            {
                "title": "Electricity & Internet Bill",
                "category": "Utilities",
                "amount": 2500.0,
                "payment_method": "Net Banking",
                "date": date(2026, 8, 12),
                "desc": "Monthly broadband and power bill",
                "goal_id": None
            },
            {
                "title": "Movies & Streaming Subscriptions",
                "category": "Entertainment",
                "amount": 2250.0,
                "payment_method": "UPI",
                "date": date(2026, 8, 18),
                "desc": "Cinema tickets & monthly streaming apps",
                "goal_id": None
            }
        ]

        for exp in expenses_data:
            db.session.add(Expense(
                title=exp["title"],
                category=exp["category"],
                amount=exp["amount"],
                payment_method=exp["payment_method"],
                account_id=account.id,
                expense_date=exp["date"],
                description=exp["desc"],
                user_id=uid,
                goal_id=exp["goal_id"]
            ))
        db.session.commit()
        print(f"  - Created {len(expenses_data)} Expense records (Total Expenses = ₹22,750.00).")

        # 7. Budget (Limit = ₹32,500.00)
        # Spent = ₹22,750.00 -> Usage = 70.0%
        # Remaining = ₹9,750.00
        budget_obj = Budget(
            monthly_budget=32500.0,
            month="August",
            year=2026,
            goal_id=education_goal.id,
            user_id=uid
        )
        db.session.add(budget_obj)
        db.session.commit()
        print(f"  - Created Budget record (Limit: ₹32,500.00, Spent: ₹22,750.00, Usage: 70.0%).")

        # 8. Investments (3 realistic records)
        investments_data = [
            {
                "name": "Nifty 50 Index Fund",
                "type": "Mutual Fund",
                "qty": 100.0,
                "invested": 20000.0,
                "current": 23000.0,
                "date": date(2026, 1, 15),
                "desc": "SIP investment in index mutual fund"
            },
            {
                "name": "TCS Stocks",
                "type": "Stock",
                "qty": 5.0,
                "invested": 15000.0,
                "current": 16500.0,
                "date": date(2026, 2, 10),
                "desc": "Bluechip IT stock holding"
            },
            {
                "name": "HDFC Bank Fixed Deposit",
                "type": "Fixed Deposit",
                "qty": 1.0,
                "invested": 15000.0,
                "current": 15750.0,
                "date": date(2026, 1, 1),
                "desc": "1-Year Fixed Deposit @ 7% p.a."
            }
        ]

        for inv in investments_data:
            db.session.add(Investment(
                instrument_name=inv["name"],
                asset_type=inv["type"],
                quantity=inv["qty"],
                invested_amount=inv["invested"],
                current_value=inv["current"],
                purchase_date=inv["date"],
                description=inv["desc"],
                user_id=uid
            ))
        db.session.commit()
        print(f"  - Created {len(investments_data)} Investment records.")

        # 9. Generate & Clean Alerts for Presentation
        # Trigger alert generator engine
        check_and_create_alerts(uid)

        # Mark minor routine alerts as read so Alert Dashboard shows 2 clean active unread alerts
        all_alerts = FinancialAlert.query.filter_by(user_id=uid).all()
        for alt in all_alerts:
            # Keep Goal Deadline Approaching and Goal Expense Linked as unread (active alerts)
            if "Deadline" in alt.title or ("Linked" in alt.title and "Higher Education" in alt.message):
                alt.is_read = False
            else:
                alt.is_read = True
        db.session.commit()

        active_alerts = get_user_alerts(uid, include_read=False)
        print(f"\n--- ACTIVE PRESENTATION ALERTS ({len(active_alerts)}) ---")
        for alt in active_alerts:
            print(f"  - [{alt.severity.upper()}] '{alt.title}': {alt.message}")

    print("\n============================================================")
    print("EXACT PRESENTATION DATASET SETUP COMPLETE!")
    print("============================================================")

if __name__ == "__main__":
    setup_exact_presentation_data()
