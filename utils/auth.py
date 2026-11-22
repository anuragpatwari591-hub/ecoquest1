"""Authentication helpers: password hashing, login check, role-based access."""
import re
from functools import wraps

from flask import flash, redirect, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from utils.database import fetch_one

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(password):
    return generate_password_hash(password)


def verify_password(password_hash, password):
    return check_password_hash(password_hash, password)


def validate_registration(name, email, password):
    """Return a list of error messages (empty list = valid)."""
    errors = []
    if not name or len(name.strip()) < 2:
        errors.append("Name must be at least 2 characters.")
    if not email or not EMAIL_RE.match(email):
        errors.append("Enter a valid email address.")
    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters.")
    return errors


def authenticate(conn, email, password):
    """Return the user row if email/password are correct and account is active, else None."""
    user = fetch_one(
        conn,
        "SELECT u.*, r.role_name FROM users u JOIN roles r ON u.role_id = r.role_id "
        "WHERE u.email = %s",
        (email.strip().lower(),),
    )
    if user and user["is_active"] and verify_password(user["password_hash"], password):
        return user
    return None


def login_user(user):
    session.clear()
    session["user_id"] = user["user_id"]
    session["name"] = user["name"]
    session["role"] = user["role_name"]


def logout_user():
    session.clear()


def home_for_role(role):
    return url_for({"student": "student.dashboard",
                    "teacher": "teacher.dashboard",
                    "admin": "admin.dashboard"}.get(role, "index"))


def login_required(*roles):
    """Decorator: user must be logged in and have one of the given roles.

    Admin may access teacher pages as well (administrators can access
    administrative functionality). Students never reach teacher/admin pages.
    """
    allowed = set(roles)

    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            role = session.get("role")
            if "user_id" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("auth.login"))
            if allowed and role not in allowed and not (role == "admin" and "teacher" in allowed):
                flash("You do not have permission to open that page.", "danger")
                return redirect(home_for_role(role))
            return view(*args, **kwargs)
        return wrapper
    return decorator
