"""Student quiz module: list, instructions, take, submit, result, history."""
from flask import (Blueprint, abort, flash, jsonify, redirect, render_template,
                   request, session, url_for)

from utils.auth import login_required
from utils.database import execute, fetch_all, fetch_one, get_db
from utils.gamification import (calculate_accuracy, calculate_quiz_xp,
                                record_activity)
from utils.ui import flash_rewards

quiz_bp = Blueprint("quiz", __name__, url_prefix="/quiz")


def load_questions(db, quiz_id):
    """Return the quiz's questions, each with its list of options."""
    questions = fetch_all(db, "SELECT * FROM questions WHERE quiz_id = %s ORDER BY question_id", (quiz_id,))
    for q in questions:
        q["options"] = fetch_all(db, "SELECT option_id, option_text, is_correct FROM options "
                                     "WHERE question_id = %s ORDER BY option_id", (q["question_id"],))
    return questions


def grade(questions, form):
    """Compare submitted answers with correct options. Returns (score, answers list).

    Each answer is (question_id, selected_option_id or None, is_correct 0/1).
    The submitted option must belong to that question, otherwise it counts as unanswered.
    """
    score, answers = 0, []
    for q in questions:
        raw = form.get(f"q_{q['question_id']}")
        selected = int(raw) if raw and raw.isdigit() else None
        valid = {o["option_id"]: o["is_correct"] for o in q["options"]}
        if selected not in valid:
            selected = None
        correct = 1 if selected is not None and valid[selected] else 0
        score += correct
        answers.append((q["question_id"], selected, correct))
    return score, answers


@quiz_bp.route("/")
@login_required("student")
def quiz_list():
    db, uid = get_db(), session["user_id"]
    quizzes = fetch_all(db, "SELECT q.*, t.name AS topic_name, t.icon, "
                            "(SELECT COUNT(*) FROM questions WHERE quiz_id = q.quiz_id) AS n_questions, "
                            "(SELECT MAX(ROUND(score * 100 / total_questions)) FROM quiz_attempts "
                            " WHERE quiz_id = q.quiz_id AND user_id = %s) AS best_pct "
                            "FROM quizzes q JOIN topics t ON q.topic_id = t.topic_id ORDER BY q.quiz_id", (uid,))
    return render_template("student/quiz_list.html", quizzes=quizzes)


@quiz_bp.route("/<int:quiz_id>")
@login_required("student")
def quiz_intro(quiz_id):
    db, uid = get_db(), session["user_id"]
    quiz = fetch_one(db, "SELECT q.*, t.name AS topic_name FROM quizzes q JOIN topics t ON q.topic_id = t.topic_id "
                         "WHERE q.quiz_id = %s", (quiz_id,))
    if not quiz:
        abort(404)
    n = fetch_one(db, "SELECT COUNT(*) AS n FROM questions WHERE quiz_id = %s", (quiz_id,))["n"]
    attempts = fetch_all(db, "SELECT * FROM quiz_attempts WHERE user_id = %s AND quiz_id = %s "
                             "ORDER BY attempted_at DESC, attempt_id DESC", (uid, quiz_id))
    return render_template("student/quiz_intro.html", quiz=quiz, n_questions=n, attempts=attempts)


@quiz_bp.route("/<int:quiz_id>/take")
@login_required("student")
def take(quiz_id):
    db = get_db()
    quiz = fetch_one(db, "SELECT * FROM quizzes WHERE quiz_id = %s", (quiz_id,))
    if not quiz:
        abort(404)
    questions = load_questions(db, quiz_id)
    if not questions:
        flash("This quiz has no questions yet.", "warning")
        return redirect(url_for("quiz.quiz_intro", quiz_id=quiz_id))
    session.pop(f"quiz_{quiz_id}", None)      # a new attempt starts with no locked answers
    for q in questions:                       # never send the correct answer to the browser
        for o in q["options"]:
            o.pop("is_correct")
    return render_template("student/quiz_take.html", quiz=quiz, questions=questions)


@quiz_bp.route("/<int:quiz_id>/submit", methods=["POST"])
@login_required("student")
def submit(quiz_id):
    db, uid = get_db(), session["user_id"]
    quiz = fetch_one(db, "SELECT * FROM quizzes WHERE quiz_id = %s", (quiz_id,))
    if not quiz:
        abort(404)
    questions = load_questions(db, quiz_id)
    if not questions:
        abort(400, "This quiz has no questions.")
    submitted = request.form.to_dict()
    for qid, option_id in session.pop(f"quiz_{quiz_id}", {}).items():
        submitted[f"q_{qid}"] = str(option_id)        # answers already revealed are locked in
    score, answers = grade(questions, submitted)
    total = len(questions)
    xp = calculate_quiz_xp(score, total)
    attempt_id = execute(db, "INSERT INTO quiz_attempts (user_id, quiz_id, score, total_questions, xp_earned) "
                             "VALUES (%s,%s,%s,%s,%s)", (uid, quiz_id, score, total, xp))
    for qid, selected, correct in answers:
        execute(db, "INSERT INTO quiz_answers (attempt_id, question_id, selected_option_id, is_correct) "
                    "VALUES (%s,%s,%s,%s)", (attempt_id, qid, selected, correct))
    result = record_activity(db, uid, xp, "quiz", f"Quiz '{quiz['title']}': {score}/{total}")
    db.commit()
    flash_rewards(result, f"Quiz complete! {score}/{total} correct.")
    return redirect(url_for("quiz.result", attempt_id=attempt_id))


@quiz_bp.route("/<int:quiz_id>/check", methods=["POST"])
@login_required("student")
def check(quiz_id):
    """Instant feedback for one question. The first choice is locked: asking again returns the same result,
    and the locked choice is what gets graded on submit (so revealing the answer cannot be used to change it)."""
    qid = request.form.get("question_id", type=int)
    option_id = request.form.get("option_id", type=int)
    db = get_db()
    options = fetch_all(db, "SELECT o.option_id, o.is_correct, q.explanation FROM options o "
                            "JOIN questions q ON o.question_id = q.question_id "
                            "WHERE q.question_id = %s AND q.quiz_id = %s", (qid, quiz_id))
    if not options or option_id not in {o["option_id"] for o in options}:
        abort(400, "Invalid question or option.")
    locked = session.get(f"quiz_{quiz_id}", {})
    chosen = locked.setdefault(str(qid), option_id)
    session[f"quiz_{quiz_id}"] = locked
    correct_id = next(o["option_id"] for o in options if o["is_correct"])
    return jsonify(chosen=chosen, correct_id=correct_id, is_correct=chosen == correct_id,
                   explanation=options[0]["explanation"] or "")


@quiz_bp.route("/result/<int:attempt_id>")
@login_required("student")
def result(attempt_id):
    db, uid = get_db(), session["user_id"]
    attempt = fetch_one(db, "SELECT qa.*, q.title FROM quiz_attempts qa JOIN quizzes q ON qa.quiz_id = q.quiz_id "
                            "WHERE qa.attempt_id = %s AND qa.user_id = %s", (attempt_id, uid))
    if not attempt:
        abort(404)
    review = fetch_all(db, """
        SELECT q.question_text, q.explanation, a.is_correct,
               so.option_text AS selected_text,
               (SELECT o.option_text FROM options o WHERE o.question_id = q.question_id AND o.is_correct = 1 LIMIT 1) AS correct_text
        FROM quiz_answers a
        JOIN questions q ON a.question_id = q.question_id
        LEFT JOIN options so ON a.selected_option_id = so.option_id
        WHERE a.attempt_id = %s ORDER BY q.question_id""", (attempt_id,))
    accuracy = calculate_accuracy(attempt["score"], attempt["total_questions"])
    return render_template("student/quiz_result.html", attempt=attempt, review=review, accuracy=accuracy)


@quiz_bp.route("/history")
@login_required("student")
def history():
    db, uid = get_db(), session["user_id"]
    attempts = fetch_all(db, "SELECT qa.*, q.title FROM quiz_attempts qa JOIN quizzes q ON qa.quiz_id = q.quiz_id "
                             "WHERE qa.user_id = %s ORDER BY qa.attempted_at DESC, qa.attempt_id DESC", (uid,))
    for a in attempts:
        a["accuracy"] = calculate_accuracy(a["score"], a["total_questions"])
    return render_template("student/quiz_history.html", attempts=attempts)
