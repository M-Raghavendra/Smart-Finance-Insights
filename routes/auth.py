from flask import Blueprint, request, render_template, redirect, url_for
from sqlalchemy import func
from models.user import User
from extensions import db, bcrypt, limiter
from flask_login import login_user, logout_user, login_required
import re


auth = Blueprint("auth", __name__)


# -------------------- Register --------------------

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    full_name = request.form.get("full_name")
    email = request.form.get("email")
    password = request.form.get("password")

    # -------------------- Required Fields --------------------

    if not full_name or not email or not password:
        return render_template(
            "register.html",
            error="Please fill in all fields.",
            full_name=full_name or "",
            email=email or ""
        ), 400

    # -------------------- Email Validation --------------------

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    email
):
        return render_template(
        "register.html",
        email_error="Please enter a valid email address.",
        full_name=full_name,
        email=email
    ), 400

    # -------------------- Password Validation --------------------

    # Minimum 8 characters
    if len(password) < 8:
        return render_template(
            "register.html",
            error="Password must be at least 8 characters long.",
            full_name=full_name,
            email=email
        ), 400

    # At least one uppercase letter
    if not re.search(r"[A-Z]", password):
        return render_template(
            "register.html",
            error="Password must contain at least one uppercase letter.",
            full_name=full_name,
            email=email
        ), 400

    # At least one lowercase letter
    if not re.search(r"[a-z]", password):
        return render_template(
            "register.html",
            error="Password must contain at least one lowercase letter.",
            full_name=full_name,
            email=email
        ), 400

    # At least one number
    if not re.search(r"\d", password):
        return render_template(
            "register.html",
            error="Password must contain at least one number.",
            full_name=full_name,
            email=email
        ), 400

    # At least one special character
    if not re.search(r"[@$!%*?&]", password):
        return render_template(
            "register.html",
            error="Password must contain at least one special character.",
            full_name=full_name,
            email=email
        ), 400

    # -------------------- Check Existing Email --------------------

    email = email.strip().lower()
    existing_user = User.query.filter(func.lower(User.email) == email).first()

    if existing_user:
        return render_template(
            "register.html",
            error="This email is already registered. Please use another email.",
            full_name=full_name,
            email=email
        ), 400

    # -------------------- Hash Password --------------------

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    # -------------------- Create User --------------------

    new_user = User(
        full_name=full_name,
        email=email,
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("auth.login"))


# -------------------- Login --------------------

@auth.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return "Email and Password are required", 400

    email = email.strip().lower()

    user = User.query.filter(func.lower(User.email) == email).first()

    if not user:
        return "User not found", 404

    if bcrypt.check_password_hash(user.password, password):

        login_user(user)

        return redirect(url_for("dashboard"))

    return "Invalid Password", 401


# -------------------- Logout --------------------

@auth.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("auth.login"))