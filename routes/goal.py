from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from extensions import db
from models.goal import Goal


goal = Blueprint(
    "goal",
    __name__
)


# =========================================================
# VIEW + ADD GOAL
# =========================================================

@goal.route("/goals", methods=["GET", "POST"])
@login_required
def goals():

    # -----------------------------------------------------
    # ADD GOAL
    # -----------------------------------------------------

    if request.method == "POST":

        goal_name = request.form.get("goal_name")
        goal_type = request.form.get("goal_type")
        

        target_amount = float(
            request.form.get("target_amount") or 0
        )

        current_amount = float(
            request.form.get("current_amount") or 0
        )

        target_date = request.form.get("target_date")

        category = request.form.get("category")
        priority = request.form.get("priority")

        # HTML form uses "description"
        # Database/model field is "notes"
        
        notes = request.form.get("notes")
        


        # -------------------------------------------------
        # Determine Status
        # -------------------------------------------------

        if (
            target_amount > 0
            and current_amount >= target_amount
        ):
            status = "Completed"
        else:
            status = "In Progress"


        # -------------------------------------------------
        # Create Goal
        # -------------------------------------------------

        new_goal = Goal(

            goal_name=goal_name,

            goal_type=goal_type,

            target_amount=target_amount,

            current_amount=current_amount,

            target_date=datetime.strptime(
                target_date,
                "%Y-%m-%d"
            ).date(),

            category=category,

            priority=priority,

            status=status,

            notes=notes,

            user_id=current_user.id
        )


        db.session.add(new_goal)

        db.session.commit()


        flash(
            "Financial goal added successfully!",
            "success"
        )


        return redirect(
            url_for("goal.goals")
        )


    # =====================================================
    # GET USER GOALS
    # =====================================================

    goals = Goal.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Goal.target_date.asc()
    ).all()


    # =====================================================
    # GOAL SUMMARY
    # =====================================================

    total_goals = len(goals)

    completed_goals = 0

    active_goals = 0


    # =====================================================
    # CALCULATE GOAL PROGRESS
    # =====================================================

    for item in goals:

        # -------------------------------------------------
        # Progress
        # -------------------------------------------------

        if item.target_amount > 0:

            item.progress = round(
                (
                    item.current_amount
                    / item.target_amount
                ) * 100,
                2
            )

        else:

            item.progress = 0


        # -------------------------------------------------
        # Maximum 100%
        # -------------------------------------------------

        if item.progress > 100:

            item.progress = 100


        # -------------------------------------------------
        # Remaining Amount
        # -------------------------------------------------

        item.remaining_amount = max(
            item.target_amount
            - item.current_amount,
            0
        )


        # -------------------------------------------------
        # Status
        # -------------------------------------------------

        if (
            item.target_amount > 0
            and item.current_amount
            >= item.target_amount
        ):

            item.status = "Completed"

            completed_goals += 1

        else:

            item.status = "In Progress"

            active_goals += 1


    # =====================================================
    # RENDER GOALS PAGE
    # =====================================================

    return render_template(
        "goals.html",

        goals=goals,

        total_goals=total_goals,

        active_goals=active_goals,

        completed_goals=completed_goals
    )


# =========================================================
# EDIT GOAL
# =========================================================

@goal.route(
    "/goals/edit/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def edit_goal(id):

    goal_data = Goal.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()


    # -----------------------------------------------------
    # UPDATE GOAL
    # -----------------------------------------------------

    if request.method == "POST":

        goal_data.goal_name = request.form.get(
            "goal_name"
        )


        goal_data.goal_type = request.form.get(
            "goal_type"
        )


        goal_data.target_amount = float(
            request.form.get("target_amount") or 0
        )


        goal_data.current_amount = float(
            request.form.get("current_amount") or 0
        )


        goal_data.target_date = datetime.strptime(
            request.form.get("target_date"),
            "%Y-%m-%d"
        ).date()


        goal_data.category = request.form.get(
            "category"
        )


        goal_data.priority = request.form.get(
            "priority"
        )


        goal_data.notes = request.form.get(
            "notes"
        )


        # -------------------------------------------------
        # Update Status
        # -------------------------------------------------

        if (
            goal_data.target_amount > 0
            and goal_data.current_amount
            >= goal_data.target_amount
        ):

            goal_data.status = "Completed"

        else:

            goal_data.status = "In Progress"


        db.session.commit()


        flash(
            "Financial goal updated successfully!",
            "success"
        )


        return redirect(
            url_for("goal.goals")
        )


    # -----------------------------------------------------
    # EDIT PAGE
    # -----------------------------------------------------

    return render_template(
        "edit_goal.html",
        goal=goal_data
    )


# =========================================================
# DELETE GOAL
# =========================================================

@goal.route(
    "/goals/delete/<int:id>"
)
@login_required
def delete_goal(id):

    goal_data = Goal.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()


    db.session.delete(
        goal_data
    )

    db.session.commit()


    flash(
        "Financial goal deleted successfully!",
        "success"
    )


    return redirect(
        url_for("goal.goals")
    )