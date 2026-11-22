"""Student pages: dashboard, learning module, leaderboard, progress, profile."""
from datetime import datetime

from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   session, url_for)

import config
from utils.auth import login_required
from utils.database import execute, fetch_all, fetch_one, get_db
from utils.gamification import (leaderboard, level_info, record_activity,
                                student_rank, topic_progress_list)

student_bp = Blueprint("student", __name__)


def _greeting():
    hour = datetime.now().hour
    return "Good Morning" if hour < 12 else "Good Afternoon" if hour < 17 else "Good Evening"


@student_bp.route("/student/dashboard")
@login_required("student")
def dashboard():
    db, uid = get_db(), session["user_id"]
    user = fetch_one(db, "SELECT * FROM users WHERE user_id = %s", (uid,))
    badge_count = fetch_one(db, "SELECT COUNT(*) AS n FROM user_badges WHERE user_id = %s", (uid,))["n"]
    progress = topic_progress_list(db, uid)
    # today's challenge: the first active challenge not yet completed today (rotates by day number)
    challenges = fetch_all(db, "SELECT c.*, t.name AS topic_name, "
                               "(SELECT COUNT(*) FROM challenge_completions cc WHERE cc.challenge_id = c.challenge_id "
                               " AND cc.user_id = %s AND cc.completed_on = CURDATE()) AS done_today "
                               "FROM challenges c JOIN topics t ON c.topic_id = t.topic_id "
                               "WHERE c.is_active = 1 ORDER BY c.challenge_id", (uid,))
    todays = None
    if challenges:
        start = datetime.now().toordinal() % len(challenges)
        rotated = challenges[start:] + challenges[:start]
        todays = next((c for c in rotated if not c["done_today"]), rotated[0])
    next_lessons = fetch_all(db, "SELECT l.lesson_id, l.title, l.difficulty, t.name AS topic_name FROM lessons l "
                                 "JOIN topics t ON l.topic_id = t.topic_id "
                                 "WHERE l.lesson_id NOT IN (SELECT lesson_id FROM user_progress WHERE user_id = %s) "
                                 "ORDER BY l.lesson_id LIMIT 4", (uid,))
    next_quizzes = fetch_all(db, "SELECT q.quiz_id, q.title, t.name AS topic_name, "
                                 "(SELECT COUNT(*) FROM questions WHERE quiz_id = q.quiz_id) AS n_questions "
                                 "FROM quizzes q JOIN topics t ON q.topic_id = t.topic_id "
                                 "WHERE q.quiz_id NOT IN (SELECT quiz_id FROM quiz_attempts WHERE user_id = %s) "
                                 "ORDER BY q.quiz_id LIMIT 4", (uid,))
    activity = fetch_all(db, "SELECT * FROM activity_log WHERE user_id = %s ORDER BY created_at DESC, log_id DESC LIMIT 6",
                         (uid,))
    return render_template("student/dashboard.html", user=user, greeting=_greeting(),
                           info=level_info(user["total_xp"]), badge_count=badge_count,
                           progress=progress, todays=todays, next_lessons=next_lessons,
                           next_quizzes=next_quizzes, activity=activity,
                           rank=student_rank(db, uid))


@student_bp.route("/student/topics")
@login_required("student")
def topics():
    db = get_db()
    rows = fetch_all(db, "SELECT t.*, (SELECT COUNT(*) FROM lessons WHERE topic_id = t.topic_id) AS n_lessons, "
                         "(SELECT COUNT(*) FROM quizzes WHERE topic_id = t.topic_id) AS n_quizzes, "
                         "(SELECT COUNT(*) FROM challenges WHERE topic_id = t.topic_id AND is_active = 1) AS n_challenges "
                         "FROM topics t ORDER BY t.topic_id")
    progress = {p["topic_id"]: p["percent"] for p in topic_progress_list(db, session["user_id"])}
    return render_template("student/topics.html", topics=rows, progress=progress)


@student_bp.route("/student/topics/<int:topic_id>")
@login_required("student")
def topic_detail(topic_id):
    db, uid = get_db(), session["user_id"]
    topic = fetch_one(db, "SELECT * FROM topics WHERE topic_id = %s", (topic_id,))
    if not topic:
        abort(404)
    lessons = fetch_all(db, "SELECT l.*, (SELECT COUNT(*) FROM user_progress up WHERE up.lesson_id = l.lesson_id "
                            "AND up.user_id = %s) AS done FROM lessons l WHERE l.topic_id = %s ORDER BY l.lesson_id",
                        (uid, topic_id))
    quizzes = fetch_all(db, "SELECT q.*, (SELECT COUNT(*) FROM questions WHERE quiz_id = q.quiz_id) AS n_questions "
                            "FROM quizzes q WHERE q.topic_id = %s", (topic_id,))
    challenges = fetch_all(db, "SELECT * FROM challenges WHERE topic_id = %s AND is_active = 1", (topic_id,))
    return render_template("student/topic_detail.html", topic=topic, lessons=lessons,
                           quizzes=quizzes, challenges=challenges)


@student_bp.route("/student/lessons/<int:lesson_id>")
@login_required("student")
def lesson(lesson_id):
    db, uid = get_db(), session["user_id"]
    row = fetch_one(db, "SELECT l.*, t.name AS topic_name, t.icon FROM lessons l "
                        "JOIN topics t ON l.topic_id = t.topic_id WHERE l.lesson_id = %s", (lesson_id,))
    if not row:
        abort(404)
    done = fetch_one(db, "SELECT 1 AS x FROM user_progress WHERE user_id = %s AND lesson_id = %s",
                     (uid, lesson_id)) is not None
    return render_template("student/lesson.html", lesson=row, points=row["key_points"].split("\n"),
                           done=done, xp=config.XP_LESSON)


@student_bp.route("/student/lessons/<int:lesson_id>/complete", methods=["POST"])
@login_required("student")
def complete_lesson(lesson_id):
    db, uid = get_db(), session["user_id"]
    row = fetch_one(db, "SELECT lesson_id, title FROM lessons WHERE lesson_id = %s", (lesson_id,))
    if not row:
        abort(404)
    if fetch_one(db, "SELECT 1 AS x FROM user_progress WHERE user_id = %s AND lesson_id = %s", (uid, lesson_id)):
        flash("You have already completed this lesson.", "info")
        return redirect(url_for("student.lesson", lesson_id=lesson_id))
    execute(db, "INSERT INTO user_progress (user_id, lesson_id) VALUES (%s,%s)", (uid, lesson_id))
    result = record_activity(db, uid, config.XP_LESSON, "lesson", f"Completed lesson: {row['title']}")
    db.commit()
    flash(f"Lesson complete! +{result['xp']} XP", "success")
    for b in result["badges"]:
        flash(f"Badge unlocked: {b['icon']} {b['name']}", "badge")
    return redirect(url_for("student.lesson", lesson_id=lesson_id))


@student_bp.route("/student/leaderboard")
@login_required("student", "teacher")
def leaderboard_page():
    db = get_db()
    institution = request.args.get("institution") or None
    class_name = request.args.get("class_name") or None
    rows = leaderboard(db, institution, class_name)
    institutions = [r["institution"] for r in fetch_all(
        db, "SELECT DISTINCT institution FROM users WHERE institution IS NOT NULL ORDER BY institution")]
    classes = [r["class_name"] for r in fetch_all(
        db, "SELECT DISTINCT class_name FROM users WHERE class_name IS NOT NULL ORDER BY class_name")]
    return render_template("student/leaderboard.html", rows=rows, institutions=institutions,
                           classes=classes, institution=institution, class_name=class_name)


@student_bp.route("/student/progress")
@login_required("student")
def progress():
    db, uid = get_db(), session["user_id"]
    topics = topic_progress_list(db, uid)
    attempts = fetch_all(db, "SELECT qa.score, qa.total_questions, qa.attempted_at, q.title FROM quiz_attempts qa "
                             "JOIN quizzes q ON qa.quiz_id = q.quiz_id WHERE qa.user_id = %s "
                             "ORDER BY qa.attempted_at, qa.attempt_id", (uid,))
    daily_xp = fetch_all(db, "SELECT DATE(created_at) AS day, SUM(xp_change) AS xp FROM activity_log "
                             "WHERE user_id = %s AND xp_change > 0 GROUP BY DATE(created_at) "
                             "ORDER BY day DESC LIMIT 14", (uid,))
    daily_xp.reverse()
    badges = fetch_all(db, "SELECT b.*, ub.earned_at FROM badges b LEFT JOIN user_badges ub "
                           "ON b.badge_id = ub.badge_id AND ub.user_id = %s ORDER BY ub.earned_at IS NULL, b.badge_id",
                       (uid,))
    history = fetch_all(db, "SELECT * FROM activity_log WHERE user_id = %s ORDER BY created_at DESC, log_id DESC LIMIT 30",
                        (uid,))
    return render_template("student/progress.html", topics=topics, attempts=attempts,
                           daily_xp=[{"day": str(d["day"]), "xp": int(d["xp"])} for d in daily_xp],
                           badges=badges, history=history)


@student_bp.route("/student/profile", methods=["GET", "POST"])
@login_required("student", "teacher", "admin")
def profile():
    db, uid = get_db(), session["user_id"]
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        institution = request.form.get("institution", "").strip() or None
        class_name = request.form.get("class_name", "").strip() or None
        if len(name) < 2:
            flash("Name must be at least 2 characters.", "danger")
        else:
            execute(db, "UPDATE users SET name = %s, institution = %s, class_name = %s WHERE user_id = %s",
                    (name, institution, class_name, uid))
            db.commit()
            session["name"] = name
            flash("Profile updated.", "success")
        return redirect(url_for("student.profile"))
    user = fetch_one(db, "SELECT * FROM users WHERE user_id = %s", (uid,))
    return render_template("student/profile.html", user=user, info=level_info(user["total_xp"]))
