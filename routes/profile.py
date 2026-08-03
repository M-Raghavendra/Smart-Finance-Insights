from flask import flash
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from models.profile import Profile
from extensions import db, bcrypt

from datetime import datetime
import os
from werkzeug.utils import secure_filename

profile = Blueprint("profile", __name__)

UPLOAD_FOLDER = "static/uploads/profile"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ----------------------------
# View / Edit Profile Page
# ----------------------------
@profile.route("/profile", methods=["GET"])
@login_required
def view_profile():

    user_profile = Profile.query.filter_by(user_id=current_user.id).first()

    mode = request.args.get("mode", "view")

    return render_template(
        "profile.html",
        user=current_user,
        profile=user_profile,
        mode=mode
    )


# ----------------------------
# Save / Update Profile
# ----------------------------
@profile.route("/profile", methods=["POST"])
@login_required
def save_profile():

    data = request.form

    user_profile = Profile.query.filter_by(user_id=current_user.id).first()

    if not user_profile:
        user_profile = Profile(user_id=current_user.id)
        db.session.add(user_profile)

    # ----------------------------
    # Upload Profile Photo
    # ----------------------------
    photo = request.files.get("profile_photo")

    if photo and photo.filename != "":

        filename = secure_filename(photo.filename)

        filename = f"user_{current_user.id}_{filename}"

        photo.save(os.path.join(UPLOAD_FOLDER, filename))

        user_profile.profile_photo = filename

    # ----------------------------
    # Save Profile Details
    # ----------------------------
    user_profile.organization_name = data.get("organization_name")
    user_profile.mobile_number = data.get("mobile_number")
    user_profile.currency = data.get("currency")
    user_profile.monthly_income = data.get("monthly_income")
    user_profile.monthly_target = data.get("monthly_target")
    user_profile.occupation = data.get("occupation")
    user_profile.income_source = data.get("income_source")

    dob = data.get("dob")

    if dob:
        user_profile.date_of_birth = datetime.strptime(
            dob,
            "%Y-%m-%d"
        ).date()

    db.session.commit()

    return redirect(url_for("profile.view_profile"))
@profile.route("/change-password", methods=["POST"])
@login_required
def change_password():

    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    # Check all fields
    if not current_password or not new_password or not confirm_password:
        flash("Please fill all password fields.", "danger")
        return redirect(url_for("profile.view_profile", mode="edit"))

    # Verify current password
    if not bcrypt.check_password_hash(current_user.password, current_password):
        flash("Current password is incorrect.", "danger")
        return redirect(url_for("profile.view_profile", mode="edit"))

    # Check password confirmation
    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for("profile.view_profile", mode="edit"))

    # Password validation
    if len(new_password) < 6:
        flash("Password must be at least 6 characters long.", "danger")
        return redirect(url_for("profile.view_profile", mode="edit"))

    # Update password
    current_user.password = bcrypt.generate_password_hash(
        new_password
    ).decode("utf-8")

    db.session.commit()

    flash("Password changed successfully!", "success")

    return redirect(url_for("profile.view_profile"))