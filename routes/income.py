from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models.income import Income

income = Blueprint("income", __name__)


@income.route("/income", methods=["GET", "POST"])
@login_required
def incomes():

    if request.method == "POST":

        title = request.form.get("title")
        source = request.form.get("source")
        amount = request.form.get("amount")
        income_date = request.form.get("income_date")
        description = request.form.get("description")

        new_income = Income(
            title=title,
            source=source,
            amount=float(amount),
            income_date=datetime.strptime(income_date, "%Y-%m-%d").date(),
            description=description,
            user_id=current_user.id
        )

        db.session.add(new_income)
        db.session.commit()

        flash("Income added successfully!", "success")

        return redirect(url_for("income.incomes"))

    incomes = Income.query.filter_by(user_id=current_user.id)\
        .order_by(Income.income_date.desc())\
        .all()

    return render_template(
        "income.html",
        incomes=incomes
    )


@income.route("/income/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_income(id):

    income_record = Income.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    if request.method == "POST":

        income_record.title = request.form.get("title")
        income_record.source = request.form.get("source")
        income_record.amount = float(request.form.get("amount"))
        income_record.income_date = datetime.strptime(
            request.form.get("income_date"),
            "%Y-%m-%d"
        ).date()
        income_record.description = request.form.get("description")

        db.session.commit()

        flash("Income updated successfully!", "success")

        return redirect(url_for("income.incomes"))

    return render_template(
        "edit_income.html",
        income=income_record
    )


@income.route("/income/delete/<int:id>")
@login_required
def delete_income(id):

    income_record = Income.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(income_record)
    db.session.commit()

    flash("Income deleted successfully!", "success")

    return redirect(url_for("income.incomes"))