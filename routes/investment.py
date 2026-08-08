from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from extensions import db
from models.investment import Investment
from models.goal import Goal


investment = Blueprint(
    "investment",
    __name__
)


# =========================================================
# INVESTMENT PORTFOLIO
# =========================================================

@investment.route("/investments", methods=["GET", "POST"])
@login_required
def investments():

    # -----------------------------------------------------
    # ADD INVESTMENT
    # -----------------------------------------------------

    if request.method == "POST":

        instrument_name = request.form.get("instrument_name")
        asset_type = request.form.get("asset_type")

        quantity = float(
            request.form.get("quantity") or 0
        )

        invested_amount = float(
            request.form.get("invested_amount") or 0
        )

        current_value = float(
            request.form.get("current_value") or 0
        )

        purchase_date = request.form.get("purchase_date")
        description = request.form.get("description")

        new_investment = Investment(
            instrument_name=instrument_name,
            asset_type=asset_type,
            quantity=quantity,
            invested_amount=invested_amount,
            current_value=current_value,
            purchase_date=datetime.strptime(
                purchase_date,
                "%Y-%m-%d"
            ).date(),
            description=description,
            user_id=current_user.id
        )

        db.session.add(new_investment)
        db.session.commit()

        flash(
            "Investment added successfully!",
            "success"
        )

        return redirect(
            url_for("investment.investments")
        )


        # -----------------------------------------------------
    # GET USER INVESTMENTS
    # -----------------------------------------------------

    investments = Investment.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Investment.purchase_date.desc()
    ).all()


    # -----------------------------------------------------
    # GET USER FINANCIAL GOALS
    # -----------------------------------------------------

    financial_goals = Goal.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Goal.target_date.asc()
    ).all()


    # -----------------------------------------------------
    # CALCULATE GOAL PROGRESS
    # -----------------------------------------------------

    for goal_item in financial_goals:

        if goal_item.target_amount > 0:

            goal_item.progress = round(
                (
                    goal_item.current_amount
                    / goal_item.target_amount
                ) * 100,
                2
            )

        else:

            goal_item.progress = 0


        if goal_item.progress > 100:
            goal_item.progress = 100


        goal_item.remaining_amount = max(
            goal_item.target_amount
            - goal_item.current_amount,
            0
        )


    # -----------------------------------------------------
    # PORTFOLIO SUMMARY
    # -----------------------------------------------------

    total_invested = sum(
        item.invested_amount
        for item in investments
    )

    total_investment_value = sum(
        item.current_value
        for item in investments
    )

    overall_returns = (
        total_investment_value
        - total_invested
    )


    if total_invested > 0:

        return_percentage = round(
            (
                overall_returns
                / total_invested
            ) * 100,
            2
        )

    else:

        return_percentage = 0


    total_holdings = len(investments)
    # -----------------------------------------------------
    # PORTFOLIO SUMMARY
    # -----------------------------------------------------

    total_invested = sum(
        item.invested_amount
        for item in investments
    )

    total_investment_value = sum(
        item.current_value
        for item in investments
    )

    overall_returns = (
        total_investment_value
        - total_invested
    )


    if total_invested > 0:

        return_percentage = round(
            (
                overall_returns
                / total_invested
            ) * 100,
            2
        )

    else:

        return_percentage = 0


    total_holdings = len(investments)


    # -----------------------------------------------------
    # ASSET ALLOCATION
    # -----------------------------------------------------

    asset_allocation = {}


    for item in investments:

        if item.asset_type not in asset_allocation:

            asset_allocation[item.asset_type] = 0

        asset_allocation[item.asset_type] += (
            item.current_value
        )


    asset_types = list(
        asset_allocation.keys()
    )


    asset_values = [
        float(value)
        for value in asset_allocation.values()
    ]


    # -----------------------------------------------------
    # ASSET ALLOCATION PERCENTAGES
    # -----------------------------------------------------

    asset_percentages = []


    if total_investment_value > 0:

        for value in asset_values:

            percentage = round(
                (
                    value
                    / total_investment_value
                ) * 100,
                2
            )

            asset_percentages.append(
                percentage
            )

    else:

        asset_percentages = [
            0
            for value in asset_values
        ]


    # -----------------------------------------------------
    # TOP HOLDINGS
    # -----------------------------------------------------

    top_holdings = sorted(
        investments,
        key=lambda item: item.current_value,
        reverse=True
    )[:5]


    # -----------------------------------------------------
    # PORTFOLIO ANALYTICS
    # -----------------------------------------------------

    best_performer = None
    worst_performer = None
    largest_holding = None
    largest_asset_type = None


    if investments:

        # Calculate return for every investment

        investment_returns = []


        for item in investments:

            if item.invested_amount > 0:

                item_return = (
                    (
                        item.current_value
                        - item.invested_amount
                    )
                    / item.invested_amount
                ) * 100

            else:

                item_return = 0


            investment_returns.append(
                (
                    item,
                    round(item_return, 2)
                )
            )


        # Best performing investment

        best_performer = max(
            investment_returns,
            key=lambda x: x[1]
        )


        # Worst performing investment

        worst_performer = min(
            investment_returns,
            key=lambda x: x[1]
        )


        # Largest holding

        largest_holding = max(
            investments,
            key=lambda item: item.current_value
        )


        # Largest asset type

        if asset_values:

            largest_asset_index = asset_values.index(
                max(asset_values)
            )

            largest_asset_type = {
                "name": asset_types[
                    largest_asset_index
                ],

                "value": asset_values[
                    largest_asset_index
                ],

                "percentage": asset_percentages[
                    largest_asset_index
                ]
            }


    # -----------------------------------------------------
    # RENDER PAGE
    # -----------------------------------------------------

    return render_template(
        "investments.html",

        investments=investments,

        total_invested=total_invested,

        total_investment_value=(
            total_investment_value
        ),

        overall_returns=overall_returns,

        return_percentage=return_percentage,

        total_holdings=total_holdings,

        asset_types=asset_types,

        asset_values=asset_values,

        asset_percentages=asset_percentages,

        top_holdings=top_holdings,

        financial_goals=financial_goals,

        best_performer=best_performer,

        worst_performer=worst_performer,

        largest_holding=largest_holding,

        largest_asset_type=largest_asset_type
    )


# =========================================================
# EDIT INVESTMENT
# =========================================================

@investment.route(
    "/investments/edit/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def edit_investment(id):

    investment_data = Investment.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()


    if request.method == "POST":

        investment_data.instrument_name = (
            request.form.get("instrument_name")
        )

        investment_data.asset_type = (
            request.form.get("asset_type")
        )

        investment_data.quantity = float(
            request.form.get("quantity") or 0
        )

        investment_data.invested_amount = float(
            request.form.get("invested_amount") or 0
        )

        investment_data.current_value = float(
            request.form.get("current_value") or 0
        )

        investment_data.purchase_date = (
            datetime.strptime(
                request.form.get("purchase_date"),
                "%Y-%m-%d"
            ).date()
        )

        investment_data.description = (
            request.form.get("description")
        )


        db.session.commit()


        flash(
            "Investment updated successfully!",
            "success"
        )


        return redirect(
            url_for("investment.investments")
        )


    return render_template(
        "edit_investment.html",
        investment=investment_data
    )


# =========================================================
# DELETE INVESTMENT
# =========================================================

@investment.route(
    "/investments/delete/<int:id>"
)
@login_required
def delete_investment(id):

    investment_data = Investment.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()


    db.session.delete(
        investment_data
    )

    db.session.commit()


    flash(
        "Investment deleted successfully!",
        "success"
    )


    return redirect(
        url_for("investment.investments")
    )