"""B.Tech study section tests (TC-51 .. TC-54)."""
from conftest import one, user_id


def test_btech_content_loaded_and_valid(db):                             # TC-51
    r = one(db, "SELECT COUNT(*) AS n FROM topics WHERE category LIKE 'B.Tech%%'")
    assert r["n"] == 13
    assert one(db, "SELECT COUNT(*) AS n FROM lessons l JOIN topics t ON l.topic_id=t.topic_id "
                   "WHERE t.category LIKE 'B.Tech%%'")["n"] == 39
    assert one(db, "SELECT COUNT(*) AS n FROM questions q JOIN quizzes z ON q.quiz_id=z.quiz_id "
                   "JOIN topics t ON z.topic_id=t.topic_id WHERE t.category LIKE 'B.Tech%%'")["n"] == 78
    assert one(db, "SELECT COUNT(*) AS n FROM topics WHERE category='Environment'")["n"] == 6


def test_seed_btech_is_idempotent(db):                                   # TC-52
    import init_db
    assert init_db.seed_btech(db) == 0                                    # nothing added the second time
    assert one(db, "SELECT COUNT(*) AS n FROM topics")["n"] == 19


def test_topics_page_groups_by_category(student):                        # TC-53
    page = student.get("/student/topics").data.decode()
    assert "B.Tech CSE/IT Core" in page and "Environment" in page and "Python Programming" in page


def test_btech_lesson_gives_xp_and_subject_badge(student, db):           # TC-54
    pid = one(db, "SELECT topic_id FROM topics WHERE name='Python Programming'")["topic_id"]
    lessons = [r["lesson_id"] for r in _all(db, "SELECT lesson_id FROM lessons WHERE topic_id=%s", (pid,))]
    for lid in lessons:
        student.post(f"/student/lessons/{lid}/complete")
    uid = user_id(db)
    assert one(db, "SELECT total_xp FROM users WHERE user_id=%s", (uid,))["total_xp"] == 30
    names = [r["name"] for r in _all(db, "SELECT b.name FROM user_badges ub JOIN badges b ON ub.badge_id=b.badge_id "
                                         "WHERE ub.user_id=%s", (uid,))]
    assert "Python Pioneer" in names


def _all(db, sql, args=None):
    db.commit()
    with db.cursor() as cur:
        cur.execute(sql, args or ())
        return cur.fetchall()
