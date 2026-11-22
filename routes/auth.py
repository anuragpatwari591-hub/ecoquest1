"""Registration, login and logout."""
import pymysql
from flask import Blueprint, flash, redirect, render_template, request, url_for

from utils.auth import (authenticate, hash_password, home_for_role, login_user,
                        logout_user, validate_registration)
from utils.database import execute, fetch_one, get_db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        institution = request.form.get("institution", "").strip() or None
        class_name = request.form.get("class_name", "").strip() or None
        errors = validate_registration(name, email, password)
        db = get_db()
        if not errors and fetch_one(db, "SELECT user_id FROM users WHERE email = %s", (email,)):
            errors.append("An account with this email already exists.")
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("register.html", form=request.form), 400
        role_id = fetch_one(db, "SELECT role_id FROM roles WHERE role_name = 'student'")["role_id"]
        try:
            execute(db, "INSERT INTO users (name, email, password_hash, role_id, institution, class_name) "
                        "VALUES (%s,%s,%s,%s,%s,%s)",
                    (name, email, hash_password(password), role_id, institution, class_name))
            db.commit()
        except pymysql.IntegrityError:
            db.rollback()
            flash("An account with this email already exists.", "danger")
            return render_template("register.html", form=request.form), 400
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html", form={})


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        user = authenticate(get_db(), email, password)
        if user:
            login_user(user)
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(home_for_role(user["role_name"]))
        flash("Invalid email or password.", "danger")
        return render_template("login.html", email=email), 401
    return render_template("login.html", email="")


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))
