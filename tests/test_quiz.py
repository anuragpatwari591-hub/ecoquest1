"""Quiz tests: scoring, XP, attempts stored in the database (TC-13 .. TC-19)."""
from conftest import one, user_id
from routes.quiz import grade


def _answers(db, quiz_id, correct_count):
    """Build form data answering the first `correct_count` questions correctly, the rest wrongly."""
    with db.cursor() as cur:
        cur.execute("SELECT question_id FROM questions WHERE quiz_id=%s ORDER BY question_id", (quiz_id,))
        qs = [r["question_id"] for r in cur.fetchall()]
        data = {}
        for i, qid in enumerate(qs):
            cur.execute("SELECT option_id FROM options WHERE question_id=%s AND is_correct=%s LIMIT 1",
                        (qid, 1 if i < correct_count else 0))
            data[f"q_{qid}"] = str(cur.fetchone()["option_id"])
    return data, len(qs)


def test_quiz_list_and_take_page_do_not_leak_answers(student):          # TC-13
    assert student.get("/quiz/").status_code == 200
    page = student.get("/quiz/1/take")
    assert page.status_code == 200 and b"is_correct" not in page.data


def test_submit_all_correct_gives_perfect_score_and_bonus(student, db):  # TC-14
    data, n = _answers(db, 3, 5)                                          # quiz 3: 5 questions
    r = student.post("/quiz/3/submit", data=data)
    assert r.status_code == 302
    attempt = one(db, "SELECT * FROM quiz_attempts ORDER BY attempt_id DESC LIMIT 1")
    assert (attempt["score"], attempt["total_questions"]) == (n, n)
    assert attempt["xp_earned"] == n * 10 + 50                            # 10 per answer + perfect bonus


def test_partial_score_xp_has_no_bonus(student, db):                     # TC-15
    data, n = _answers(db, 3, 3)
    student.post("/quiz/3/submit", data=data)
    attempt = one(db, "SELECT * FROM quiz_attempts ORDER BY attempt_id DESC LIMIT 1")
    assert attempt["score"] == 3 and attempt["xp_earned"] == 30


def test_all_wrong_gives_zero(student, db):                              # TC-16
    data, n = _answers(db, 3, 0)
    student.post("/quiz/3/submit", data=data)
    attempt = one(db, "SELECT * FROM quiz_attempts ORDER BY attempt_id DESC LIMIT 1")
    assert attempt["score"] == 0 and attempt["xp_earned"] == 0


def test_attempt_and_answers_stored_and_user_xp_updated(student, db):    # TC-17
    data, n = _answers(db, 3, 4)
    student.post("/quiz/3/submit", data=data)
    uid = user_id(db)
    attempt = one(db, "SELECT attempt_id FROM quiz_attempts WHERE user_id=%s", (uid,))
    count = one(db, "SELECT COUNT(*) AS n FROM quiz_answers WHERE attempt_id=%s", (attempt["attempt_id"],))["n"]
    assert count == n
    assert one(db, "SELECT total_xp FROM users WHERE user_id=%s", (uid,))["total_xp"] == 40


def test_result_page_shows_score_and_review(student, db):                # TC-18
    data, n = _answers(db, 3, 4)
    r = student.post("/quiz/3/submit", data=data, follow_redirects=True)
    assert b"Quiz Complete" in r.data and b"Answer review" in r.data and b"4/5" in r.data


def test_grade_ignores_option_from_other_question(db):                   # TC-19 (tamper check)
    from routes.quiz import load_questions
    questions = load_questions(db, 3)
    foreign = questions[1]["options"][0]["option_id"]
    score, answers = grade(questions, {f"q_{questions[0]['question_id']}": str(foreign)})
    assert score == 0 and answers[0][1] is None


def test_student_cannot_view_another_students_result(student, client, db):  # TC-20
    data, _ = _answers(db, 3, 5)
    student.post("/quiz/3/submit", data=data)
    attempt_id = one(db, "SELECT attempt_id FROM quiz_attempts LIMIT 1")["attempt_id"]
    other = client.application.test_client()
    other.post("/login", data={"email": "riya@ecoquest.test", "password": "Student@123"})
    # Riya is not in the seeded test DB (no sample activity) but is a demo user, so login works
    assert other.get(f"/quiz/result/{attempt_id}").status_code == 404
