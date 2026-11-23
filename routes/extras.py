"""Quest Map, certificates, password change/reset, CSV exports and announcements."""
import csv
import io
from datetime import date

from flask import (Blueprint, Response, abort, flash, redirect, render_template,
                   request, session, url_for)

from utils.auth import hash_password, login_required, verify_password
from utils.database import execute, fetch_all, fetch_one, get_db
from utils.gamification import level_info, quest_map

extras_bp = Blueprint("extras", __name__)

CERT_TIERS = [(10, "Eco Champion"), (5, "Eco Guardian"), (3, "Eco Learner")]


def certificate_title(level):
    for min_level, title in CERT_TIERS:
        if level >= min_level:
            return title
    return None


# ------------------------------------------------------------------ Quest Map
@extras_bp.route("/student/map")
@login_required("student")
def quest_map_page():
    return render_template("student/quest_map.html", topics=quest_map(get_db(), session["user_id"]))


# ------------------------------------------------------------------ certificate
@extras_bp.route("/student/certificate")
@login_required("student")
def certificate():
    db, uid = get_db(), session["user_id"]
    user = fetch_one(db, "SELECT * FROM users WHERE user_id = %s", (uid,))
    info = level_info(user["total_xp"])
    title = certificate_title(info["level"])
    if not title:
        flash("Reach Level 3 to unlock your first EcoQuest certificate!", "info")
        return redirect(url_for("student.dashboard"))
    badges = fetch_one(db, "SELECT COUNT(*) AS n FROM user_badges WHERE user_id = %s", (uid,))["n"]
    lessons = fetch_one(db, "SELECT COUNT(*) AS n FROM user_progress WHERE user_id = %s", (uid,))["n"]
    return render_template("student/certificate.html", user=user, info=info, title=title, badges=badges,
                           lessons=lessons, today=date.today())


# ------------------------------------------------------------------ password
@extras_bp.route("/account/password", methods=["GET", "POST"])
@login_required("student", "teacher", "admin")
def change_password():
    if request.method == "POST":
        db, uid = get_db(), session["user_id"]
        user = fetch_one(db, "SELECT password_hash FROM users WHERE user_id = %s", (uid,))
        current, new, confirm = (request.form.get(k, "") for k in ("current", "new", "confirm"))
        if not verify_password(user["password_hash"], current):
            flash("Your current password is incorrect.", "danger")
        elif len(new) < 6:
            flash("The new password must be at least 6 characters.", "danger")
        elif new != confirm:
            flash("The new passwords do not match.", "danger")
        else:
            execute(db, "UPDATE users SET password_hash = %s WHERE user_id = %s", (hash_password(new), uid))
            db.commit()
            flash("Password changed successfully.", "success")
            return redirect(url_for("student.profile"))
    return render_template("student/password.html")


@extras_bp.route("/admin/users/<int:user_id>/reset-password", methods=["POST"])
@login_required("admin")
def reset_password(user_id):
    new = request.form.get("new_password", "")
    if len(new) < 6:
        flash("The new password must be at least 6 characters.", "danger")
    else:
        db = get_db()
        execute(db, "UPDATE users SET password_hash = %s WHERE user_id = %s", (hash_password(new), user_id))
        db.commit()
        flash("Password reset. Share the new password with the user privately.", "success")
    return redirect(url_for("admin.users"))


# ------------------------------------------------------------------ CSV exports
def csv_response(filename, header, rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(header)
    w.writerows(rows)
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})


@extras_bp.route("/student/progress.csv")
@login_required("student")
def progress_csv():
    rows = fetch_all(get_db(), "SELECT created_at, activity, description, xp_change FROM activity_log WHERE user_id = %s "
                               "ORDER BY created_at, log_id", (session["user_id"],))
    return csv_response("my_ecoquest_progress.csv", ["date_time", "activity", "description", "xp"],
                        [(r["created_at"], r["activity"], r["description"], r["xp_change"]) for r in rows])


@extras_bp.route("/teacher/students.csv")
@login_required("teacher")
def students_csv():
    rows = fetch_all(get_db(), """
        SELECT u.name, u.email, u.institution, u.class_name, u.total_xp, u.streak,
               (SELECT COUNT(*) FROM user_progress p WHERE p.user_id = u.user_id) AS lessons,
               (SELECT COUNT(*) FROM quiz_attempts a WHERE a.user_id = u.user_id) AS attempts,
               (SELECT COALESCE(ROUND(AVG(score * 100 / total_questions)), 0) FROM quiz_attempts a WHERE a.user_id = u.user_id) AS avg_pct,
               (SELECT COUNT(*) FROM user_badges b WHERE b.user_id = u.user_id) AS badges
        FROM users u JOIN roles r ON u.role_id = r.role_id WHERE r.role_name = 'student' ORDER BY u.class_name, u.name""")
    return csv_response("ecoquest_students.csv",
                        ["name", "email", "institution", "class", "level", "xp", "streak", "lessons", "quiz_attempts", "avg_score_pct", "badges"],
                        [(r["name"], r["email"], r["institution"] or "", r["class_name"] or "", level_info(r["total_xp"])["level"],
                          r["total_xp"], r["streak"], r["lessons"], r["attempts"], int(r["avg_pct"]), r["badges"]) for r in rows])


# ------------------------------------------------------------------ announcements
@extras_bp.route("/teacher/announcements", methods=["GET", "POST"])
@login_required("teacher")
def announcements():
    db = get_db()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        message = request.form.get("message", "").strip()
        if not title or not message:
            flash("Title and message are required.", "danger")
        else:
            execute(db, "INSERT INTO announcements (title, message, created_by) VALUES (%s,%s,%s)",
                    (title[:120], message[:500], session["user_id"]))
            db.commit()
            flash("Announcement posted to all students.", "success")
        return redirect(url_for("extras.announcements"))
    rows = fetch_all(db, "SELECT a.*, u.name AS author FROM announcements a LEFT JOIN users u ON a.created_by = u.user_id "
                         "ORDER BY a.created_at DESC, a.announcement_id DESC")
    return render_template("teacher/announcements.html", announcements=rows)


@extras_bp.route("/teacher/announcements/<int:aid>/delete", methods=["POST"])
@login_required("teacher")
def announcement_delete(aid):
    db = get_db()
    if not fetch_one(db, "SELECT 1 AS x FROM announcements WHERE announcement_id = %s", (aid,)):
        abort(404)
    execute(db, "DELETE FROM announcements WHERE announcement_id = %s", (aid,))
    db.commit()
    flash("Announcement removed.", "info")
    return redirect(url_for("extras.announcements"))
