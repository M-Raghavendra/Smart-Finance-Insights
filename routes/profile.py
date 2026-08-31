from flask import flash
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from models.profile import Profile
from extensions import db, bcrypt

from datetime import datetime
import os
from werkzeug.utils import secure_filename


profile = Blueprint("profile", __name__)


UPLOAD_FOLDER = "static/uploads/profile_pictures"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# VIEW / EDIT PROFILE PAGE
# =========================================================

@profile.route("/profile", methods=["GET"])
@login_required
def view_profile():

    user_profile = Profile.query.filter_by(
        user_id=current_user.id
    ).first()

    mode = request.args.get(
        "mode",
        "view"
    )

    return render_template(
        "profile.html",
        user=current_user,
        profile=user_profile,
        mode=mode
    )


# =========================================================
# SAVE / UPDATE PROFILE
# =========================================================

@profile.route("/profile", methods=["POST"])
@login_required
def save_profile():

    data = request.form

    user_profile = Profile.query.filter_by(
        user_id=current_user.id
    ).first()


    # -----------------------------------------------------
    # Create profile if it doesn't exist
    # -----------------------------------------------------

    if not user_profile:

        user_profile = Profile(
            user_id=current_user.id
        )

        db.session.add(user_profile)


    # =====================================================
    # UPLOAD PROFILE PHOTO
    # =====================================================

    photo = request.files.get("profile_photo")

    if photo and photo.filename != "":
        ext = photo.filename.rsplit(".", 1)[-1].lower() if "." in photo.filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            flash("Invalid file format. Allowed formats: JPG, JPEG, PNG, WEBP.", "danger")
            return redirect(url_for("profile.view_profile", mode="edit"))

        # File size validation (5MB)
        photo.seek(0, os.SEEK_END)
        file_size = photo.tell()
        photo.seek(0)
        if file_size > MAX_CONTENT_LENGTH:
            flash("File size exceeds 5 MB limit.", "danger")
            return redirect(url_for("profile.view_profile", mode="edit"))

        sec_name = secure_filename(photo.filename)
        timestamp = int(datetime.utcnow().timestamp())
        filename = f"user_{current_user.id}_{timestamp}_{sec_name}"

        save_path = os.path.join(UPLOAD_FOLDER, filename)
        photo.save(save_path)

        relative_img_path = f"uploads/profile_pictures/{filename}"
        user_profile.profile_photo = filename
        current_user.profile_image = relative_img_path


    # =====================================================
    # SAVE PROFILE DETAILS & THEME PREFERENCE
    # =====================================================

    theme_pref = data.get("theme_preference")
    if theme_pref in ["light", "dark"]:
        current_user.theme_preference = theme_pref

    user_profile.organization_name = (
        data.get("organization_name") or ""
    )

    user_profile.mobile_number = (
        data.get("mobile_number") or ""
    )

    user_profile.currency = (
        data.get("currency") or ""
    )

    user_profile.occupation = (
        data.get("occupation") or ""
    )

    user_profile.income_source = (
        data.get("income_source") or ""
    )


    # =====================================================
    # MONTHLY INCOME
    # =====================================================

    monthly_income = data.get(
        "monthly_income"
    )

    if monthly_income and monthly_income.strip():

        try:

            user_profile.monthly_income = float(
                monthly_income
            )

        except ValueError:

            flash(
                "Monthly income must be a valid number.",
                "danger"
            )

            return redirect(
                url_for(
                    "profile.view_profile",
                    mode="edit"
                )
            )

    else:

        user_profile.monthly_income = 0


    # =====================================================
    # MONTHLY TARGET
    # =====================================================

    monthly_target = data.get(
        "monthly_target"
    )

    if monthly_target and monthly_target.strip():

        try:

            user_profile.monthly_target = float(
                monthly_target
            )

        except ValueError:

            flash(
                "Monthly target must be a valid number.",
                "danger"
            )

            return redirect(
                url_for(
                    "profile.view_profile",
                    mode="edit"
                )
            )

    else:

        user_profile.monthly_target = 0


    # =====================================================
    # DATE OF BIRTH
    # =====================================================

    dob = data.get(
        "dob"
    )

    if dob and dob.strip():

        try:

            user_profile.date_of_birth = (
                datetime.strptime(
                    dob,
                    "%Y-%m-%d"
                ).date()
            )

        except ValueError:

            flash(
                "Invalid date of birth.",
                "danger"
            )

            return redirect(
                url_for(
                    "profile.view_profile",
                    mode="edit"
                )
            )

    else:

        user_profile.date_of_birth = None


    # =====================================================
    # SAVE TO DATABASE
    # =====================================================

    db.session.commit()


    flash(
        "Profile updated successfully!",
        "success"
    )


    return redirect(
        url_for(
            "profile.view_profile"
        )
    )


# =========================================================
# CHANGE PASSWORD
# =========================================================

@profile.route(
    "/change-password",
    methods=["POST"]
)
@login_required
def change_password():

    current_password = request.form.get(
        "current_password"
    )

    new_password = request.form.get(
        "new_password"
    )

    confirm_password = request.form.get(
        "confirm_password"
    )


    # -----------------------------------------------------
    # Check all fields
    # -----------------------------------------------------

    if (
        not current_password
        or not new_password
        or not confirm_password
    ):

        flash(
            "Please fill all password fields.",
            "danger"
        )

        return redirect(
            url_for(
                "profile.view_profile",
                mode="edit"
            )
        )


    # -----------------------------------------------------
    # Verify current password
    # -----------------------------------------------------

    if not bcrypt.check_password_hash(
        current_user.password,
        current_password
    ):

        flash(
            "Current password is incorrect.",
            "danger"
        )

        return redirect(
            url_for(
                "profile.view_profile",
                mode="edit"
            )
        )


    # -----------------------------------------------------
    # Check password confirmation
    # -----------------------------------------------------

    if new_password != confirm_password:

        flash(
            "New passwords do not match.",
            "danger"
        )

        return redirect(
            url_for(
                "profile.view_profile",
                mode="edit"
            )
        )


    # -----------------------------------------------------
    # Password validation
    # -----------------------------------------------------

    if len(new_password) < 6:

        flash(
            "Password must be at least 6 characters long.",
            "danger"
        )

        return redirect(
            url_for(
                "profile.view_profile",
                mode="edit"
            )
        )


    # -----------------------------------------------------
    # Update password
    # -----------------------------------------------------

    current_user.password = (
        bcrypt.generate_password_hash(
            new_password
        ).decode("utf-8")
    )


    db.session.commit()


    flash(
        "Password changed successfully!",
        "success"
    )


    return redirect(
        url_for(
            "profile.view_profile"
        )
    )


# =========================================================
# INSTANT THEME PREFERENCE PERSISTENCE
# =========================================================

@profile.route("/profile/theme", methods=["POST"])
@login_required
def update_theme():
    req_data = request.get_json(silent=True) or request.form
    theme_choice = req_data.get("theme_preference")

    if theme_choice in ["light", "dark"]:
        current_user.theme_preference = theme_choice
        db.session.commit()
        return {"status": "success", "theme_preference": theme_choice}, 200

    return {"status": "error", "message": "Invalid theme selection"}, 400