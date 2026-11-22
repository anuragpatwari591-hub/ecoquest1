"""Admin pages: statistics, users, topics, lessons, badges (quizzes/challenges reuse teacher pages)."""
import pymysql
from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   session, url_for)

from utils.auth import hash_password, login_required, validate_registration
from utils.database import execute, fetch_all, fetch_one, get_db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

BADGE_RULES = {
    "lessons": "Lessons completed",
    "quizzes": "Quizzes completed",
    "topic_challenges": "Challenges completed in a topic",
    "topic_activity": "Lessons + challenges in a topic",
    "games": "Mini-games played (days)",
    "streak": "Day streak",
    "xp": "Total XP",
}


@admin_bp.route("/dashboard")
@login_required("admin")
def dashboard():
    db = get_db()
    stats = fetch_one(db, """
        SELECT
          (SELECT COUNT(*) FROM users) AS users,
          (SELECT COUNT(*) FROM users u JOIN roles r ON u.role_id = r.role_id WHERE r.role_name = 'student') AS students,
          (SELECT COUNT(*) FROM users u JOIN roles r ON u.role_id = r.role_id WHERE r.role_name = 'teacher') AS teachers,
          (SELECT COUNT(*) FROM topics) AS topics,
          (SELECT COUNT(*) FROM lessons) AS lessons,
          (SELECT COUNT(*) FROM quizzes) AS quizzes,
          (SELECT COUNT(*) FROM challenges) AS challenges,
          (SELECT COUNT(*) FROM quiz_attempts) AS attempts,
          (SELECT COUNT(*) FROM challenge_completions) AS completions""")
    by_role = fetch_all(db, "SELECT r.role_name, COUNT(u.user_id) AS n FROM roles r "
                            "LEFT JOIN users u ON u.role_id = r.role_id GROUP BY r.role_id, r.role_name ORDER BY r.role_id")
    content = fetch_all(db, "SELECT t.name, (SELECT COUNT(*) FROM lessons WHERE topic_id = t.topic_id) AS lessons, "
                            "(SELECT COUNT(*) FROM quizzes WHERE topic_id = t.topic_id) AS quizzes, "
                            "(SELECT COUNT(*) FROM challenges WHERE topic_id = t.topic_id) AS challenges "
                            "FROM topics t ORDER BY t.topic_id")
    charts = {"roles": {"labels": [r["role_name"].title() for r in by_role], "values": [r["n"] for r in by_role]},
              "content": {"labels": [c["name"] for c in content],
                          "lessons": [c["lessons"] for c in content],
                          "quizzes": [c["quizzes"] for c in content],
                          "challenges": [c["challenges"] for c in content]}}
    return render_template("admin/dashboard.html", stats=stats, charts=charts)


# ------------------------------------------------------------------ users
@admin_bp.route("/users", methods=["GET", "POST"])
@login_required("admin")
def users():
    db = get_db()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "")
        errors = validate_registration(name, email, password)
        role_row = fetch_one(db, "SELECT role_id FROM roles WHERE role_name = %s", (role,))
        if not role_row:
            errors.append("Choose a valid role.")
        if not errors and fetch_one(db, "SELECT 1 AS x FROM users WHERE email = %s", (email,)):
            errors.append("That email is already registered.")
        if errors:
            for e in errors:
                flash(e, "danger")
        else:
            execute(db, "INSERT INTO users (name, email, password_hash, role_id, institution, class_name) "
                        "VALUES (%s,%s,%s,%s,%s,%s)",
                    (name, email, hash_password(password), role_row["role_id"],
                     request.form.get("institution", "").strip() or None,
                     request.form.get("class_name", "").strip() or None))
            db.commit()
            flash(f"{role.title()} account created.", "success")
        return redirect(url_for("admin.users"))
    role_filter = request.args.get("role")
    sql = ("SELECT u.user_id, u.name, u.email, u.institution, u.class_name, u.total_xp, u.is_active, r.role_name "
           "FROM users u JOIN roles r ON u.role_id = r.role_id")
    args = []
    if role_filter in ("student", "teacher", "admin"):
        sql += " WHERE r.role_name = %s"
        args.append(role_filter)
    rows = fetch_all(db, sql + " ORDER BY r.role_id DESC, u.name", args)
    return render_template("admin/users.html", users=rows, role_filter=role_filter)


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required("admin")
def user_toggle(user_id):
    if user_id == session["user_id"]:
        flash("You cannot deactivate your own account.", "danger")
    else:
        db = get_db()
        execute(db, "UPDATE users SET is_active = 1 - is_active WHERE user_id = %s", (user_id,))
        db.commit()
        flash("User status updated.", "info")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required("admin")
def user_delete(user_id):
    if user_id == session["user_id"]:
        flash("You cannot delete your own account.", "danger")
    else:
        db = get_db()
        execute(db, "DELETE FROM users WHERE user_id = %s", (user_id,))
        db.commit()
        flash("User deleted (their progress was removed too).", "info")
    return redirect(url_for("admin.users"))


# ------------------------------------------------------------------ topics
@admin_bp.route("/topics", methods=["GET", "POST"])
@login_required("admin")
def topics():
    db = get_db()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        icon = request.form.get("icon", "").strip() or "🌍"
        desc = request.form.get("description", "").strip()
        topic_id = request.form.get("topic_id", type=int)
        if not name or not desc:
            flash("Name and description are required.", "danger")
        else:
            try:
                if topic_id:
                    execute(db, "UPDATE topics SET name=%s, icon=%s, description=%s WHERE topic_id=%s",
                            (name[:80], icon[:10], desc, topic_id))
                else:
                    execute(db, "INSERT INTO topics (name, icon, description) VALUES (%s,%s,%s)",
                            (name[:80], icon[:10], desc))
                db.commit()
                flash("Topic saved.", "success")
            except pymysql.IntegrityError:
                db.rollback()
                flash("A topic with that name already exists.", "danger")
        return redirect(url_for("admin.topics"))
    rows = fetch_all(db, "SELECT t.*, (SELECT COUNT(*) FROM lessons WHERE topic_id = t.topic_id) AS n_lessons "
                         "FROM topics t ORDER BY t.topic_id")
    return render_template("admin/topics.html", topics=rows)


@admin_bp.route("/topics/<int:topic_id>/delete", methods=["POST"])
@login_required("admin")
def topic_delete(topic_id):
    db = get_db()
    execute(db, "DELETE FROM topics WHERE topic_id = %s", (topic_id,))
    db.commit()
    flash("Topic and all its lessons, quizzes and challenges were deleted.", "info")
    return redirect(url_for("admin.topics"))


# ------------------------------------------------------------------ lessons
@admin_bp.route("/lessons")
@login_required("admin")
def lessons():
    db = get_db()
    rows = fetch_all(db, "SELECT l.lesson_id, l.title, l.difficulty, t.name AS topic_name FROM lessons l "
                         "JOIN topics t ON l.topic_id = t.topic_id ORDER BY t.topic_id, l.lesson_id")
    return render_template("admin/lessons.html", lessons=rows)


@admin_bp.route("/lessons/new", methods=["GET", "POST"])
@admin_bp.route("/lessons/<int:lesson_id>/edit", methods=["GET", "POST"])
@login_required("admin")
def lesson_form(lesson_id=None):
    db = get_db()
    lesson = fetch_one(db, "SELECT * FROM lessons WHERE lesson_id = %s", (lesson_id,)) if lesson_id else None
    if lesson_id and not lesson:
        abort(404)
    if request.method == "POST":
        f = request.form
        fields = [f.get("title", "").strip(), f.get("introduction", "").strip(), f.get("explanation", "").strip(),
                  f.get("key_points", "").strip(), f.get("eco_tip", "").strip()]
        topic_id, difficulty = f.get("topic_id", type=int), f.get("difficulty")
        if (not all(fields) or difficulty not in ("Beginner", "Intermediate", "Advanced")
                or not fetch_one(db, "SELECT 1 AS x FROM topics WHERE topic_id = %s", (topic_id,))):
            flash("All fields are required.", "danger")
            lesson = dict(f)
        else:
            title, intro, expl, points, tip = fields
            if lesson_id:
                execute(db, "UPDATE lessons SET topic_id=%s, title=%s, difficulty=%s, introduction=%s, explanation=%s, "
                            "key_points=%s, eco_tip=%s WHERE lesson_id=%s",
                        (topic_id, title[:150], difficulty, intro, expl, points, tip[:300], lesson_id))
            else:
                execute(db, "INSERT INTO lessons (topic_id, title, difficulty, introduction, explanation, key_points, eco_tip) "
                            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (topic_id, title[:150], difficulty, intro, expl, points, tip[:300]))
            db.commit()
            flash("Lesson saved.", "success")
            return redirect(url_for("admin.lessons"))
    topics = fetch_all(db, "SELECT topic_id, name FROM topics ORDER BY name")
    return render_template("admin/lesson_form.html", lesson=lesson, topics=topics)


@admin_bp.route("/lessons/<int:lesson_id>/delete", methods=["POST"])
@login_required("admin")
def lesson_delete(lesson_id):
    db = get_db()
    execute(db, "DELETE FROM lessons WHERE lesson_id = %s", (lesson_id,))
    db.commit()
    flash("Lesson deleted.", "info")
    return redirect(url_for("admin.lessons"))


# ------------------------------------------------------------------ badges
@admin_bp.route("/badges", methods=["GET", "POST"])
@login_required("admin")
def badges():
    db = get_db()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        desc = request.form.get("description", "").strip()
        icon = request.form.get("icon", "").strip() or "🏅"
        rule = request.form.get("rule_type")
        value = request.form.get("rule_value", type=int)
        topic_id = request.form.get("topic_id", type=int) or None
        needs_topic = rule in ("topic_challenges", "topic_activity")
        if (not name or not desc or rule not in BADGE_RULES or not value or value < 1
                or (needs_topic and not topic_id)):
            flash("Fill all fields (topic rules also need a topic).", "danger")
        else:
            try:
                execute(db, "INSERT INTO badges (name, description, icon, rule_type, rule_value, topic_id) "
                            "VALUES (%s,%s,%s,%s,%s,%s)",
                        (name[:60], desc[:255], icon[:10], rule, value, topic_id if needs_topic else None))
                db.commit()
                flash("Badge created. It is awarded automatically when the rule is met.", "success")
            except pymysql.IntegrityError:
                db.rollback()
                flash("A badge with that name already exists.", "danger")
        return redirect(url_for("admin.badges"))
    rows = fetch_all(db, "SELECT b.*, t.name AS topic_name, "
                         "(SELECT COUNT(*) FROM user_badges WHERE badge_id = b.badge_id) AS n_earned "
                         "FROM badges b LEFT JOIN topics t ON b.topic_id = t.topic_id ORDER BY b.badge_id")
    topics = fetch_all(db, "SELECT topic_id, name FROM topics ORDER BY name")
    return render_template("admin/badges.html", badges=rows, topics=topics, rules=BADGE_RULES)


@admin_bp.route("/badges/<int:badge_id>/delete", methods=["POST"])
@login_required("admin")
def badge_delete(badge_id):
    db = get_db()
    execute(db, "DELETE FROM badges WHERE badge_id = %s", (badge_id,))
    db.commit()
    flash("Badge deleted.", "info")
    return redirect(url_for("admin.badges"))
