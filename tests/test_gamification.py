"""Gamification tests: level, XP, streak, badges, leaderboard, progress (TC-21 .. TC-32)."""
from datetime import date, timedelta

import pytest

from conftest import one, user_id
from utils import gamification as g


@pytest.mark.parametrize("xp,level", [(0, 1), (99, 1), (100, 2), (199, 2), (250, 3), (1000, 11)])
def test_level_calculation(xp, level):                                    # TC-21
    assert g.calculate_level(xp) == level


def test_level_info_progress():                                          # TC-22
    info = g.level_info(250)
    assert info["level"] == 3 and info["xp_into_level"] == 50 and info["xp_to_next"] == 50 and info["percent"] == 50


@pytest.mark.parametrize("score,total,xp", [(8, 10, 80), (10, 10, 150), (0, 10, 0), (5, 5, 100)])
def test_quiz_xp_formula(score, total, xp):                              # TC-23
    assert g.calculate_quiz_xp(score, total) == xp


def test_streak_rules():                                                 # TC-24
    today = date(2026, 5, 10)
    assert g.next_streak(None, 0, today) == 1                            # first activity
    assert g.next_streak(today, 4, today) == 4                           # same day: unchanged
    assert g.next_streak(today - timedelta(days=1), 4, today) == 5       # consecutive day
    assert g.next_streak(today - timedelta(days=2), 4, today) == 1       # missed a day: reset


def test_seven_day_streak_awards_bonus_xp(db):                           # TC-25
    uid = user_id(db)
    today = date.today()
    with db.cursor() as cur:
        cur.execute("UPDATE users SET streak = 6, last_active = %s WHERE user_id = %s", (today - timedelta(days=1), uid))
    bonus = g.update_streak(db, uid, today)
    db.commit()
    assert bonus == 100
    row = one(db, "SELECT streak, total_xp FROM users WHERE user_id=%s", (uid,))
    assert row["streak"] == 7 and row["total_xp"] == 100


def test_complete_lesson_awards_xp_and_first_badge(student, db):         # TC-26
    student.post("/student/lessons/1/complete")
    uid = user_id(db)
    assert one(db, "SELECT total_xp FROM users WHERE user_id=%s", (uid,))["total_xp"] == 10
    assert one(db, "SELECT COUNT(*) AS n FROM user_progress WHERE user_id=%s", (uid,))["n"] == 1
    badge = one(db, "SELECT b.name FROM user_badges ub JOIN badges b ON ub.badge_id=b.badge_id WHERE ub.user_id=%s", (uid,))
    assert badge["name"] == "Green Beginner"


def test_lesson_completion_is_not_repeatable(student, db):                # TC-27
    student.post("/student/lessons/1/complete")
    student.post("/student/lessons/1/complete")
    assert one(db, "SELECT total_xp FROM users WHERE user_id=%s", (user_id(db),))["total_xp"] == 10


def test_eco_champion_badge_at_1000_xp(db):                              # TC-28
    uid = user_id(db)
    with db.cursor() as cur:
        cur.execute("UPDATE users SET total_xp = 1000 WHERE user_id = %s", (uid,))
    earned = [b["name"] for b in g.check_badges(db, uid)]
    assert "Eco Champion" in earned
    assert g.check_badges(db, uid) == []                                 # not awarded twice


def test_eco_learner_badge_after_five_quizzes(db):                       # TC-29
    uid = user_id(db)
    with db.cursor() as cur:
        for _ in range(5):
            cur.execute("INSERT INTO quiz_attempts (user_id, quiz_id, score, total_questions, xp_earned) VALUES (%s,1,3,5,30)", (uid,))
    assert "Eco Learner" in [b["name"] for b in g.check_badges(db, uid)]


def test_leaderboard_sorted_by_xp_desc(db):                              # TC-30
    ids = {e: user_id(db, e) for e in ("student@ecoquest.test", "riya@ecoquest.test", "kabir@ecoquest.test")}
    with db.cursor() as cur:
        cur.execute("UPDATE users SET total_xp=300 WHERE user_id=%s", (ids["riya@ecoquest.test"],))
        cur.execute("UPDATE users SET total_xp=500 WHERE user_id=%s", (ids["kabir@ecoquest.test"],))
        cur.execute("UPDATE users SET total_xp=100 WHERE user_id=%s", (ids["student@ecoquest.test"],))
    rows = g.leaderboard(db)
    xps = [r["total_xp"] for r in rows]
    assert xps == sorted(xps, reverse=True)
    assert rows[0]["name"] == "Kabir Mehta" and rows[0]["rank"] == 1
    assert g.student_rank(db, ids["student@ecoquest.test"]) == 3
    assert all(r["user_id"] not in (user_id(db, "teacher@ecoquest.test"),) for r in rows)   # students only


def test_leaderboard_class_filter(db):                                   # TC-31
    rows = g.leaderboard(db, class_name="Class 10-B")
    assert [r["name"] for r in rows] == ["Kabir Mehta"]


def test_topic_progress_percentage(student, db):                         # TC-32
    uid = user_id(db)
    before = {p["name"]: p["percent"] for p in g.topic_progress_list(db, uid)}
    assert before["Climate Change"] == 0
    student.post("/student/lessons/1/complete")
    db.commit()                      # start a fresh snapshot to see the committed change
    after = {p["name"]: p["percent"] for p in g.topic_progress_list(db, uid)}
    assert after["Climate Change"] > 0
