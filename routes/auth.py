from flask import Blueprint, request, render_template, redirect, url_for
from models.user import User
from extensions import db, bcrypt
from flask_login import login_user, logout_user, login_required

auth = Blueprint("auth", __name__)


# -------------------- Register --------------------

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    full_name = request.form.get("full_name")
    email = request.form.get("email")
    password = request.form.get("password")

    if not full_name or not email or not password:
        return "All fields are required", 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return "Email already registered", 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

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
def login():

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return "Email and Password are required", 400

    user = User.query.filter_by(email=email).first()

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