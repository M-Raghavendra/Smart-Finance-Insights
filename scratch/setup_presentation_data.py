import os
import sys
from datetime import date, datetime

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

def setup_exact_minimal_presentation_data():
    print("============================================================")
    print("SETTING UP MINIMAL PRESENTATION DATASET (VICKY)")
    print("============================================================")

    with app.app_context():
        init_db_schema()

        # 1. User check
        user = User.query.filter_by(email="vicky@gmail.com").first()
        if not user:
            pw_hash = bcrypt.generate_password_hash("Vicky@123").decode("utf-8")
            user = User(full_name="Vicky", email="vicky@gmail.com", password=pw_hash)
            db.session.add(user)
            db.session.commit()
        
        uid = user.id
        print(f"Target User: {user.full_name} ({user.email}) [ID: {uid}]")

        # 2. Clear old test records for Vicky
        old_budgets = Budget.query.filter_by(user_id=uid).all()
        for b in old_budgets:
            b.goal_id = None
        db.session.commit()

        Expense.query.filter_by(user_id=uid).delete()
        Income.query.filter_by(user_id=uid).delete()
        Budget.query.filter_by(user_id=uid).delete()
        Investment.query.filter_by(user_id=uid).delete()
        if Goal.query.filter_by(user_id=uid).count() > 0:
            GoalPart.query.filter(GoalPart.goal_id.in_([g.id for g in Goal.query.filter_by(user_id=uid).all()])).delete(synchronize_session=False)
        Goal.query.filter_by(user_id=uid).delete()
        Account.query.filter_by(user_id=uid).delete()
        FinancialAlert.query.filter_by(user_id=uid).delete()
        db.session.commit()
        print("  - Purged old records.")

        # 3. Create Account (Initial Balance ₹2,000 -> Final Balance ₹9,250 after Net ₹7,250)
        account = Account(
            account_name="Student Savings Account",
            account_type="Savings",
            balance=2000.0,
            description="Primary bank account for stipend and daily savings",
            user_id=uid
        )
        db.session.add(account)
        db.session.commit()

        # 4. Income: ₹12,000
        salary_income = Income(
            title="Monthly Stipend / Salary",
            source="Salary",
            amount=12000.0,
            income_date=date(2026, 8, 1),
            description="Monthly income",
            user_id=uid
        )
        db.session.add(salary_income)
        account.balance += 12000.0
        db.session.commit()
        print("  - Created 1 Income record (Salary = ₹12,000).")

        # 5. Goals (Exactly 3 Goals)
        # Goal 1: New Laptop (Target ₹30,000, Saved ₹12,000)
        # Goal 2: Trip (Target ₹10,000, Saved ₹3,000)
        # Goal 3: Emergency Fund (Target ₹15,000, Saved ₹7,500)
        goals_data = [
            {"name": "New Laptop", "type": "Short Term", "target": 30000.0, "current": 12000.0, "date": date(2026, 12, 31), "category": "Shopping", "priority": "High"},
            {"name": "Trip", "type": "Short Term", "target": 10000.0, "current": 3000.0, "date": date(2026, 11, 15), "category": "Travel", "priority": "Medium"},
            {"name": "Emergency Fund", "type": "Long Term", "target": 15000.0, "current": 7500.0, "date": date(2027, 6, 30), "category": "Savings", "priority": "High"}
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
                notes=f"Student presentation goal: {g['name']}",
                user_id=uid
            )
            db.session.add(g_obj)
            created_goals.append(g_obj)
        db.session.commit()
        print(f"  - Created {len(created_goals)} presentation goals.")

        laptop_goal = created_goals[0]
        trip_goal = created_goals[1]
        emergency_goal = created_goals[2]

        # 6. Expenses (Exactly 7 Expense Records)
        # Goal-Linked Expenses (4 records):
        # Laptop Goal (Total ₹2,000): Laptop Advance Payment ₹1,500 + Laptop Accessories ₹500
        # Trip Goal (Total ₹2,000): Bus Ticket ₹800 + Hotel Advance ₹1,200
        # Emergency Fund: 0 expenses (₹0)

        # Regular Expenses (3 records):
        # Food ₹300, Transport ₹200, Mobile Recharge ₹250 (Total ₹750)

        expenses_data = [
            # Goal: New Laptop (Total ₹2,000)
            {"title": "Laptop Advance Payment", "category": "Shopping", "amount": 1500.0, "date": date(2026, 8, 15), "goal_id": laptop_goal.id},
            {"title": "Laptop Accessories", "category": "Shopping", "amount": 500.0, "date": date(2026, 8, 18), "goal_id": laptop_goal.id},

            # Goal: Trip (Total ₹2,000)
            {"title": "Bus Ticket", "category": "Travel", "amount": 800.0, "date": date(2026, 8, 12), "goal_id": trip_goal.id},
            {"title": "Hotel Advance", "category": "Travel", "amount": 1200.0, "date": date(2026, 8, 16), "goal_id": trip_goal.id},

            # Regular Non-Goal Expenses (Total ₹750)
            {"title": "Food & Snacks", "category": "Food", "amount": 300.0, "date": date(2026, 8, 3), "goal_id": None},
            {"title": "Local Commute", "category": "Transport", "amount": 200.0, "date": date(2026, 8, 7), "goal_id": None},
            {"title": "Mobile Recharge", "category": "Bills", "amount": 250.0, "date": date(2026, 8, 10), "goal_id": None}
        ]

        for exp in expenses_data:
            db.session.add(Expense(
                title=exp["title"],
                category=exp["category"],
                amount=exp["amount"],
                payment_method="Card",
                account_id=account.id,
                expense_date=exp["date"],
                description=f"Presentation expense for {exp['title']}",
                user_id=uid,
                goal_id=exp["goal_id"]
            ))
        account.balance -= 4750.0 # Total August Expenses ₹4,750
        db.session.commit()
        print(f"  - Created {len(expenses_data)} expense records (Goal-Linked: ₹4,000, Regular: ₹750, Total: ₹4,750).")

        # 7. Budgets (Shopping ₹2,000, Travel ₹1,500, Food ₹1,000)
        budgets_data = [
            {"monthly_budget": 2000.0, "month": "August", "year": 2026, "goal_id": laptop_goal.id},
            {"monthly_budget": 1500.0, "month": "August", "year": 2026, "goal_id": trip_goal.id},
            {"monthly_budget": 1000.0, "month": "August", "year": 2026, "goal_id": None}
        ]

        for b in budgets_data:
            db.session.add(Budget(
                monthly_budget=b["monthly_budget"],
                month=b["month"],
                year=b["year"],
                goal_id=b["goal_id"],
                user_id=uid
            ))
        db.session.commit()
        print(f"  - Created {len(budgets_data)} budgets.")

        # 8. Trigger Alerts
        check_and_create_alerts(uid)
        alerts = get_user_alerts(uid, include_read=False)
        print(f"\n--- GENERATED PRESENTATION ALERTS ({len(alerts)}) ---")
        for alt in alerts:
            print(f"  - [{alt.severity.upper()}] '{alt.title}': {alt.message}")

    print("\n============================================================")
    print("MINIMAL PRESENTATION DATASET SETUP COMPLETE!")
    print("============================================================")

if __name__ == "__main__":
    setup_exact_minimal_presentation_data()
