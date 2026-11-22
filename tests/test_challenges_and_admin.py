"""Challenge, teacher/admin and database tests (TC-33 .. TC-45)."""
from conftest import one, user_id


def test_complete_challenge_awards_xp(student, db):                       # TC-33
    student.post("/challenges/1/complete")                                # "Carry a reusable water bottle" = 20 XP
    uid = user_id(db)
    assert one(db, "SELECT total_xp FROM users WHERE user_id=%s", (uid,))["total_xp"] == 20
    assert one(db, "SELECT COUNT(*) AS n FROM challenge_completions WHERE user_id=%s", (uid,))["n"] == 1


def test_duplicate_challenge_same_day_blocked(student, db):               # TC-34
    student.post("/challenges/1/complete")
    r = student.post("/challenges/1/complete", follow_redirects=True)
    assert b"already completed" in r.data
    assert one(db, "SELECT total_xp FROM users WHERE user_id=%s", (user_id(db),))["total_xp"] == 20


def test_unique_key_blocks_duplicate_in_database(db):                     # TC-35
    import pymysql
    import pytest
    uid = user_id(db)
    with db.cursor() as cur:
        cur.execute("INSERT INTO challenge_completions (user_id, challenge_id, completed_on, xp_earned) VALUES (%s,1,CURDATE(),20)", (uid,))
        with pytest.raises(pymysql.IntegrityError):
            cur.execute("INSERT INTO challenge_completions (user_id, challenge_id, completed_on, xp_earned) VALUES (%s,1,CURDATE(),20)", (uid,))
    db.rollback()


def test_recycling_hero_after_five_waste_challenges(student, db):         # TC-36
    for cid in (1, 2, 3, 4, 5):                                           # five Waste Management challenges
        student.post(f"/challenges/{cid}/complete")
    names = [r["name"] for r in _badges(db, user_id(db))]
    assert "Recycling Hero" in names


def _badges(db, uid):
    db.commit()
    with db.cursor() as cur:
        cur.execute("SELECT b.name FROM user_badges ub JOIN badges b ON ub.badge_id=b.badge_id WHERE ub.user_id=%s", (uid,))
        return cur.fetchall()


def test_inactive_challenge_cannot_be_completed(student, db):             # TC-37
    with db.cursor() as cur:
        cur.execute("UPDATE challenges SET is_active = 0 WHERE challenge_id = 2")
    db.commit()
    assert student.post("/challenges/2/complete").status_code == 404
    with db.cursor() as cur:
        cur.execute("UPDATE challenges SET is_active = 1 WHERE challenge_id = 2")
    db.commit()


def test_teacher_creates_quiz_with_question(teacher, db):                 # TC-38
    r = teacher.post("/teacher/quizzes/new", data={"title": "TEST Quiz", "description": "d", "topic_id": "1"})
    assert r.status_code == 302
    quiz_id = one(db, "SELECT quiz_id FROM quizzes WHERE title='TEST Quiz'")["quiz_id"]
    teacher.post(f"/teacher/quizzes/{quiz_id}/questions", data={
        "question_text": "2+2?", "option1": "3", "option2": "4", "option3": "5", "option4": "6", "correct": "2"})
    q = one(db, "SELECT question_id FROM questions WHERE quiz_id=%s", (quiz_id,))
    correct = one(db, "SELECT option_text FROM options WHERE question_id=%s AND is_correct=1", (q["question_id"],))
    assert correct["option_text"] == "4"
    assert one(db, "SELECT COUNT(*) AS n FROM options WHERE question_id=%s", (q["question_id"],))["n"] == 4


def test_teacher_question_validation(teacher, db):                        # TC-39
    teacher.post("/teacher/quizzes/new", data={"title": "TEST Quiz 2", "description": "d", "topic_id": "1"})
    quiz_id = one(db, "SELECT quiz_id FROM quizzes WHERE title='TEST Quiz 2'")["quiz_id"]
    teacher.post(f"/teacher/quizzes/{quiz_id}/questions", data={"question_text": "Incomplete?", "option1": "a"})
    assert one(db, "SELECT COUNT(*) AS n FROM questions WHERE quiz_id=%s", (quiz_id,))["n"] == 0


def test_teacher_creates_challenge(teacher, db):                          # TC-40
    teacher.post("/teacher/challenges", data={"title": "TEST Challenge", "description": "d", "topic_id": "1",
                                              "difficulty": "Easy", "xp_reward": "25"})
    assert one(db, "SELECT xp_reward FROM challenges WHERE title='TEST Challenge'")["xp_reward"] == 25


def test_teacher_dashboard_and_student_pages_render(teacher):             # TC-41
    for url in ("/teacher/dashboard", "/teacher/students", "/teacher/quizzes", "/teacher/challenges",
                f"/teacher/students/3", "/student/leaderboard"):
        assert teacher.get(url).status_code == 200, url


def test_admin_creates_user_with_hashed_password(admin, db):              # TC-42
    admin.post("/admin/users", data={"name": "New Teacher", "email": "nt@example.com", "password": "abcdef", "role": "teacher"})
    row = one(db, "SELECT u.password_hash, r.role_name FROM users u JOIN roles r ON u.role_id=r.role_id WHERE email='nt@example.com'")
    assert row["role_name"] == "teacher" and row["password_hash"] != "abcdef"


def test_admin_cannot_delete_or_disable_self(admin, db):                  # TC-43
    admin_id = user_id(db, "admin@ecoquest.test")
    admin.post(f"/admin/users/{admin_id}/delete")
    admin.post(f"/admin/users/{admin_id}/toggle")
    row = one(db, "SELECT is_active FROM users WHERE user_id=%s", (admin_id,))
    assert row is not None and row["is_active"] == 1


def test_admin_adds_badge_and_deleting_topic_cascades(admin, db):         # TC-44
    admin.post("/admin/topics", data={"name": "TEST Topic", "icon": "🧪", "description": "temp"})
    tid = one(db, "SELECT topic_id FROM topics WHERE name='TEST Topic'")["topic_id"]
    admin.post("/admin/lessons/new", data={"title": "TEST lesson", "topic_id": str(tid), "difficulty": "Beginner",
                                          "introduction": "i", "explanation": "e", "key_points": "k", "eco_tip": "t"})
    assert one(db, "SELECT COUNT(*) AS n FROM lessons WHERE topic_id=%s", (tid,))["n"] == 1
    admin.post(f"/admin/topics/{tid}/delete")
    assert one(db, "SELECT COUNT(*) AS n FROM lessons WHERE topic_id=%s", (tid,))["n"] == 0   # ON DELETE CASCADE


def test_seed_data_meets_requirements(db):                                # TC-45
    counts = one(db, "SELECT (SELECT COUNT(*) FROM topics) t, (SELECT COUNT(*) FROM lessons) l, "
                     "(SELECT COUNT(*) FROM quizzes) qz, (SELECT COUNT(*) FROM questions) q, "
                     "(SELECT COUNT(*) FROM challenges) c, (SELECT COUNT(*) FROM badges) b, (SELECT COUNT(*) FROM roles) r")
    assert counts["t"] >= 6 and counts["l"] >= 12 and counts["qz"] >= 6
    assert counts["q"] >= 30 and counts["c"] >= 10 and counts["b"] >= 6 and counts["r"] == 3
    bad = one(db, "SELECT COUNT(*) AS n FROM questions q WHERE (SELECT COUNT(*) FROM options o WHERE o.question_id=q.question_id)<>4 "
                  "OR (SELECT COUNT(*) FROM options o WHERE o.question_id=q.question_id AND o.is_correct=1)<>1")
    assert bad["n"] == 0                                                  # every question: 4 options, exactly 1 correct


def test_foreign_key_rejects_orphan_attempt(db):                          # TC-46
    import pymysql
    import pytest
    with db.cursor() as cur, pytest.raises(pymysql.IntegrityError):
        cur.execute("INSERT INTO quiz_attempts (user_id, quiz_id, score, total_questions) VALUES (99999, 1, 1, 1)")
    db.rollback()
