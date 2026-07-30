from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from models.profile import Profile
from extensions import db

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