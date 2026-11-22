"""Teacher pages (also open to admins): dashboard, students, quizzes, questions, challenges."""
from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   session, url_for)

from utils.auth import login_required
from utils.database import execute, fetch_all, fetch_one, get_db
from utils.gamification import level_info, topic_progress_list

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")


def teaching_stats(db):
    return fetch_one(db, """
        SELECT
          (SELECT COUNT(*) FROM users u JOIN roles r ON u.role_id = r.role_id
            WHERE r.role_name = 'student' AND u.is_active = 1) AS total_students,
          (SELECT COUNT(*) FROM users u JOIN roles r ON u.role_id = r.role_id
            WHERE r.role_name = 'student' AND u.is_active = 1
              AND u.last_active >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)) AS active_students,
          (SELECT COALESCE(ROUND(AVG(score * 100 / total_questions)), 0) FROM quiz_attempts) AS avg_score,
          (SELECT COUNT(*) FROM quiz_attempts) AS quiz_attempts,
          (SELECT COUNT(*) FROM challenge_completions) AS challenges_completed""")


@teacher_bp.route("/dashboard")
@login_required("teacher")
def dashboard():
    db = get_db()
    quiz_perf = fetch_all(db, "SELECT q.title, ROUND(AVG(a.score * 100 / a.total_questions)) AS avg_pct, "
                              "COUNT(a.attempt_id) AS attempts FROM quizzes q "
                              "LEFT JOIN quiz_attempts a ON q.quiz_id = a.quiz_id GROUP BY q.quiz_id, q.title "
                              "ORDER BY q.quiz_id")
    topic_completion = fetch_all(db, "SELECT t.name, COUNT(up.progress_id) AS completed FROM topics t "
                                     "LEFT JOIN lessons l ON l.topic_id = t.topic_id "
                                     "LEFT JOIN user_progress up ON up.lesson_id = l.lesson_id "
                                     "GROUP BY t.topic_id, t.name ORDER BY t.topic_id")
    challenge_counts = fetch_all(db, "SELECT t.name, COUNT(cc.completion_id) AS completed FROM topics t "
                                     "LEFT JOIN challenges c ON c.topic_id = t.topic_id "
                                     "LEFT JOIN challenge_completions cc ON cc.challenge_id = c.challenge_id "
                                     "GROUP BY t.topic_id, t.name ORDER BY t.topic_id")
    participation = fetch_all(db, "SELECT DATE(created_at) AS day, COUNT(DISTINCT user_id) AS students "
                                  "FROM activity_log WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) "
                                  "AND activity IN ('lesson','quiz','challenge') GROUP BY DATE(created_at) "
                                  "ORDER BY day")
    charts = {
        "quiz": {"labels": [r["title"] for r in quiz_perf], "values": [int(r["avg_pct"] or 0) for r in quiz_perf]},
        "topics": {"labels": [r["name"] for r in topic_completion], "values": [r["completed"] for r in topic_completion]},
        "challenges": {"labels": [r["name"] for r in challenge_counts], "values": [r["completed"] for r in challenge_counts]},
        "participation": {"labels": [str(r["day"]) for r in participation], "values": [r["students"] for r in participation]},
    }
    return render_template("teacher/dashboard.html", stats=teaching_stats(db), charts=charts)


@teacher_bp.route("/students")
@login_required("teacher")
def students():
    db = get_db()
    class_name = request.args.get("class_name") or None
    sql = ("SELECT u.user_id, u.name, u.email, u.institution, u.class_name, u.total_xp, u.streak, u.last_active, "
           "(SELECT COUNT(*) FROM quiz_attempts a WHERE a.user_id = u.user_id) AS attempts, "
           "(SELECT COALESCE(ROUND(AVG(score * 100 / total_questions)), 0) FROM quiz_attempts a WHERE a.user_id = u.user_id) AS avg_pct, "
           "(SELECT COUNT(*) FROM user_progress p WHERE p.user_id = u.user_id) AS lessons_done "
           "FROM users u JOIN roles r ON u.role_id = r.role_id WHERE r.role_name = 'student'")
    args = []
    if class_name:
        sql += " AND u.class_name = %s"
        args.append(class_name)
    rows = fetch_all(db, sql + " ORDER BY u.name", args)
    for r in rows:
        r["level"] = level_info(r["total_xp"])["level"]
    classes = [r["class_name"] for r in fetch_all(
        db, "SELECT DISTINCT class_name FROM users WHERE class_name IS NOT NULL ORDER BY class_name")]
    return render_template("teacher/students.html", students=rows, classes=classes, class_name=class_name)


@teacher_bp.route("/students/<int:user_id>")
@login_required("teacher")
def student_detail(user_id):
    db = get_db()
    student = fetch_one(db, "SELECT u.* FROM users u JOIN roles r ON u.role_id = r.role_id "
                            "WHERE u.user_id = %s AND r.role_name = 'student'", (user_id,))
    if not student:
        abort(404)
    attempts = fetch_all(db, "SELECT qa.*, q.title FROM quiz_attempts qa JOIN quizzes q ON qa.quiz_id = q.quiz_id "
                             "WHERE qa.user_id = %s ORDER BY qa.attempted_at DESC", (user_id,))
    completions = fetch_all(db, "SELECT cc.*, c.title FROM challenge_completions cc "
                                "JOIN challenges c ON cc.challenge_id = c.challenge_id WHERE cc.user_id = %s "
                                "ORDER BY cc.completed_on DESC", (user_id,))
    badges = fetch_all(db, "SELECT b.* FROM user_badges ub JOIN badges b ON ub.badge_id = b.badge_id "
                           "WHERE ub.user_id = %s", (user_id,))
    return render_template("teacher/student_detail.html", student=student, info=level_info(student["total_xp"]),
                           attempts=attempts, completions=completions, badges=badges,
                           progress=topic_progress_list(db, user_id))


# ------------------------------------------------------------------ quizzes
@teacher_bp.route("/quizzes")
@login_required("teacher")
def quizzes():
    db = get_db()
    rows = fetch_all(db, "SELECT q.*, t.name AS topic_name, "
                         "(SELECT COUNT(*) FROM questions WHERE quiz_id = q.quiz_id) AS n_questions, "
                         "(SELECT COUNT(*) FROM quiz_attempts WHERE quiz_id = q.quiz_id) AS n_attempts "
                         "FROM quizzes q JOIN topics t ON q.topic_id = t.topic_id ORDER BY q.quiz_id DESC")
    topics = fetch_all(db, "SELECT topic_id, name FROM topics ORDER BY name")
    return render_template("teacher/quizzes.html", quizzes=rows, topics=topics)


@teacher_bp.route("/quizzes/new", methods=["POST"])
@login_required("teacher")
def quiz_create():
    db = get_db()
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    topic_id = request.form.get("topic_id", type=int)
    if not title or not description or not topic_id or not fetch_one(
            db, "SELECT 1 AS x FROM topics WHERE topic_id = %s", (topic_id,)):
        flash("Title, description and topic are required.", "danger")
        return redirect(url_for("teacher.quizzes"))
    quiz_id = execute(db, "INSERT INTO quizzes (topic_id, title, description, created_by) VALUES (%s,%s,%s,%s)",
                      (topic_id, title[:150], description, session["user_id"]))
    db.commit()
    flash("Quiz created. Now add questions.", "success")
    return redirect(url_for("teacher.quiz_questions", quiz_id=quiz_id))


@teacher_bp.route("/quizzes/<int:quiz_id>/questions", methods=["GET", "POST"])
@login_required("teacher")
def quiz_questions(quiz_id):
    db = get_db()
    quiz = fetch_one(db, "SELECT * FROM quizzes WHERE quiz_id = %s", (quiz_id,))
    if not quiz:
        abort(404)
    if request.method == "POST":
        text = request.form.get("question_text", "").strip()
        opts = [request.form.get(f"option{i}", "").strip() for i in range(1, 5)]
        correct = request.form.get("correct", type=int)
        explanation = request.form.get("explanation", "").strip() or None
        if not text or not all(opts) or correct not in (1, 2, 3, 4):
            flash("Enter the question, all four options and choose the correct one.", "danger")
        else:
            qid = execute(db, "INSERT INTO questions (quiz_id, question_text, explanation) VALUES (%s,%s,%s)",
                          (quiz_id, text[:500], explanation))
            for i, opt in enumerate(opts, start=1):
                execute(db, "INSERT INTO options (question_id, option_text, is_correct) VALUES (%s,%s,%s)",
                        (qid, opt[:300], 1 if i == correct else 0))
            db.commit()
            flash("Question added.", "success")
        return redirect(url_for("teacher.quiz_questions", quiz_id=quiz_id))
    questions = fetch_all(db, "SELECT * FROM questions WHERE quiz_id = %s ORDER BY question_id", (quiz_id,))
    for q in questions:
        q["options"] = fetch_all(db, "SELECT * FROM options WHERE question_id = %s ORDER BY option_id", (q["question_id"],))
    return render_template("teacher/questions.html", quiz=quiz, questions=questions)


@teacher_bp.route("/questions/<int:question_id>/delete", methods=["POST"])
@login_required("teacher")
def question_delete(question_id):
    db = get_db()
    q = fetch_one(db, "SELECT quiz_id FROM questions WHERE question_id = %s", (question_id,))
    if not q:
        abort(404)
    execute(db, "DELETE FROM questions WHERE question_id = %s", (question_id,))
    db.commit()
    flash("Question deleted.", "info")
    return redirect(url_for("teacher.quiz_questions", quiz_id=q["quiz_id"]))


@teacher_bp.route("/quizzes/<int:quiz_id>/delete", methods=["POST"])
@login_required("teacher")
def quiz_delete(quiz_id):
    db = get_db()
    quiz = fetch_one(db, "SELECT * FROM quizzes WHERE quiz_id = %s", (quiz_id,))
    if not quiz:
        abort(404)
    if session["role"] != "admin" and quiz["created_by"] != session["user_id"]:
        flash("Teachers can delete only quizzes they created.", "danger")
        return redirect(url_for("teacher.quizzes"))
    execute(db, "DELETE FROM quizzes WHERE quiz_id = %s", (quiz_id,))
    db.commit()
    flash("Quiz deleted.", "info")
    return redirect(url_for("teacher.quizzes"))


# ------------------------------------------------------------------ challenges
@teacher_bp.route("/challenges", methods=["GET", "POST"])
@login_required("teacher")
def challenges():
    db = get_db()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        topic_id = request.form.get("topic_id", type=int)
        difficulty = request.form.get("difficulty", "Easy")
        xp = request.form.get("xp_reward", type=int)
        if (not title or not description or difficulty not in ("Easy", "Medium", "Hard")
                or xp is None or not 1 <= xp <= 200
                or not fetch_one(db, "SELECT 1 AS x FROM topics WHERE topic_id = %s", (topic_id,))):
            flash("Please fill all fields (XP must be between 1 and 200).", "danger")
        else:
            execute(db, "INSERT INTO challenges (topic_id, title, description, difficulty, xp_reward, created_by) "
                        "VALUES (%s,%s,%s,%s,%s,%s)",
                    (topic_id, title[:150], description, difficulty, xp, session["user_id"]))
            db.commit()
            flash("Challenge created.", "success")
        return redirect(url_for("teacher.challenges"))
    rows = fetch_all(db, "SELECT c.*, t.name AS topic_name, "
                         "(SELECT COUNT(*) FROM challenge_completions WHERE challenge_id = c.challenge_id) AS n_done "
                         "FROM challenges c JOIN topics t ON c.topic_id = t.topic_id ORDER BY c.challenge_id DESC")
    topics = fetch_all(db, "SELECT topic_id, name FROM topics ORDER BY name")
    return render_template("teacher/challenges.html", challenges=rows, topics=topics)


@teacher_bp.route("/challenges/<int:challenge_id>/toggle", methods=["POST"])
@login_required("teacher")
def challenge_toggle(challenge_id):
    db = get_db()
    execute(db, "UPDATE challenges SET is_active = 1 - is_active WHERE challenge_id = %s", (challenge_id,))
    db.commit()
    flash("Challenge status updated.", "info")
    return redirect(url_for("teacher.challenges"))
