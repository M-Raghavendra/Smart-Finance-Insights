from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from extensions import db
from models.account import Account

account = Blueprint("account", __name__)


# View + Add Account

@account.route("/accounts", methods=["GET", "POST"])
@login_required
def accounts():

    if request.method == "POST":

        account_name = request.form.get("account_name")
        account_type = request.form.get("account_type")
        balance_raw = request.form.get("balance")
        description = request.form.get("description")

        if not account_name or not account_type or balance_raw is None or str(balance_raw).strip() == "":
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("account.accounts"))

        try:
            balance = float(balance_raw)
        except (ValueError, TypeError):
            flash("Invalid account balance format.", "danger")
            return redirect(url_for("account.accounts"))

        new_account = Account(
            account_name=account_name,
            account_type=account_type,
            balance=balance,
            description=description,
            user_id=current_user.id
        )

        db.session.add(new_account)
        db.session.commit()

        flash("Account added successfully!", "success")

        return redirect(url_for("account.accounts"))

    accounts = Account.query.filter_by(
        user_id=current_user.id
    ).order_by(Account.created_at.desc()).all()

    return render_template(
        "accounts.html",
        accounts=accounts
    )



# Edit Account

@account.route("/accounts/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_account(id):

    account_data = Account.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    if request.method == "POST":

        account_name = request.form.get("account_name")
        account_type = request.form.get("account_type")
        balance_raw = request.form.get("balance")
        description = request.form.get("description")

        if not account_name or not account_type or balance_raw is None or str(balance_raw).strip() == "":
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("account.edit_account", id=id))

        try:
            balance = float(balance_raw)
        except (ValueError, TypeError):
            flash("Invalid account balance format.", "danger")
            return redirect(url_for("account.edit_account", id=id))

        account_data.account_name = account_name
        account_data.account_type = account_type
        account_data.balance = balance
        account_data.description = description

        db.session.commit()

        flash("Account updated successfully!", "success")

        return redirect(url_for("account.accounts"))

    return render_template(
        "edit_account.html",
        account=account_data
    )



# Delete Account

@account.route("/accounts/delete/<int:id>")
@login_required
def delete_account(id):

    account_data = Account.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(account_data)
    db.session.commit()

    flash("Account deleted successfully!", "success")

    return redirect(url_for("account.accounts"))