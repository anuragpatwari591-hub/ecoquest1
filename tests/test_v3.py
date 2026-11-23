"""v3 features: Eco Pulse, Quest Map, weekly goal, certificate, passwords, CSV, announcements, new games (TC-61 .. TC-75)."""
import pytest

from conftest import one, user_id
from utils import gamification as g
from utils import pulse
from utils.games import GAMES

FAKE = {"aqi": 93, "pm25": 69.2, "pm10": 69.8, "time": "2026-11-23 17:30",
        "history": [{"day": "2026-11-22", "aqi": 120}, {"day": "2026-11-23", "aqi": 95}], "live": True}


@pytest.fixture()
def live_air(monkeypatch):
    monkeypatch.setattr(pulse, "get_air", lambda max_age=1800: dict(FAKE))


@pytest.fixture()
def no_air(monkeypatch):
    monkeypatch.setattr(pulse, "get_air", lambda max_age=1800: None)


def test_aqi_categories_and_groups():                                       # TC-61
    assert pulse.category(40)["name"] == "Good"
    assert pulse.category(93)["name"] == "Moderate"
    assert pulse.category(140)["name"] == "Unhealthy for sensitive groups"
    assert pulse.category(180)["name"] == "Unhealthy"
    assert pulse.category(350)["name"] == "Hazardous"
    assert [pulse.guess_group(a) for a in (50, 100, 101, 150, 151)] == ["good", "good", "sensitive", "sensitive", "bad"]
    assert pulse.daily_fact() in pulse.FACTS


def test_pulse_hides_aqi_until_prediction(student, live_air):               # TC-62
    page = student.get("/pulse/").data.decode()
    assert "Today's air is hidden" in page and "aqi-num" not in page


def test_pulse_correct_prediction_awards_xp_once(student, db, live_air):    # TC-63
    student.post("/pulse/guess", data={"guess": "good"})                     # 93 -> good
    student.post("/pulse/guess", data={"guess": "bad"})                      # second try same day: ignored
    uid = user_id(db)
    assert one(db, "SELECT total_xp FROM users WHERE user_id=%s", (uid,))["total_xp"] == 15
    assert one(db, "SELECT COUNT(*) AS n FROM activity_log WHERE user_id=%s AND activity='pulse'", (uid,))["n"] == 1
    page = student.get("/pulse/").data.decode()
    assert "aqi-num" in page and "Moderate" in page


def test_pulse_wrong_prediction_gives_checkin_xp(student, db, live_air):    # TC-64
    student.post("/pulse/guess", data={"guess": "bad"})
    assert one(db, "SELECT total_xp FROM users WHERE user_id=%s", (user_id(db),))["total_xp"] == 5


def test_pulse_offline_awards_nothing(student, db, no_air):                 # TC-65
    student.post("/pulse/guess", data={"guess": "good"})
    assert one(db, "SELECT total_xp FROM users WHERE user_id=%s", (user_id(db),))["total_xp"] == 0
    assert student.get("/pulse/").status_code == 200


def test_quest_map_and_difficulty_levels(student, db):                      # TC-66
    assert student.get("/student/map").status_code == 200
    levels = one(db, "SELECT COUNT(DISTINCT difficulty) AS n FROM quizzes")["n"]
    assert levels == 3                                                       # Beginner, Intermediate, Advanced
    topics = g.quest_map(db, user_id(db))
    assert all(t["quizzes"] and t["lessons"] for t in topics)


def test_weekly_goal_bonus_once(db):                                        # TC-67
    uid = user_id(db)
    g.record_activity(db, uid, 150, "lesson", "test xp 1")
    assert g.weekly_progress(db, uid)["claimed"] is False
    r = g.record_activity(db, uid, 60, "lesson", "test xp 2")
    assert r["weekly_bonus"] == 50
    r2 = g.record_activity(db, uid, 10, "lesson", "test xp 3")
    assert r2["weekly_bonus"] == 0
    db.commit()


def test_certificate_locked_then_unlocked(student, db):                     # TC-68
    assert student.get("/student/certificate").status_code == 302
    with db.cursor() as cur:
        cur.execute("UPDATE users SET total_xp = 450 WHERE user_id = %s", (user_id(db),))
    db.commit()
    page = student.get("/student/certificate").data.decode()
    assert "Certificate of Achievement" in page and "Eco Learner" in page


def test_change_password_flow(client, db):                                  # TC-69
    client.post("/register", data={"name": "Pass Test", "email": "pass@example.com", "password": "first1"})
    bad = client.post("/account/password", data={"current": "wrong", "new": "second2", "confirm": "second2"})
    assert b"incorrect" in bad.data
    client.post("/account/password", data={"current": "first1", "new": "second2", "confirm": "second2"})
    client.get("/logout")
    r = client.post("/login", data={"email": "pass@example.com", "password": "second2"})
    assert r.status_code == 302 and "/student/dashboard" in r.location


def test_admin_reset_password(admin, client, db):                           # TC-70
    admin.post("/admin/users", data={"name": "Reset Me", "email": "reset@example.com", "password": "abcdef", "role": "student"})
    uid = user_id(db, "reset@example.com")
    admin.post(f"/admin/users/{uid}/reset-password", data={"new_password": "newpass9"})
    admin.get("/logout")
    r = client.post("/login", data={"email": "reset@example.com", "password": "newpass9"})
    assert r.status_code == 302


def test_csv_exports(student, app):                                # TC-71
    r = student.get("/student/progress.csv")
    assert r.mimetype == "text/csv" and r.data.decode().startswith("date_time,activity")
    t = app.test_client()
    t.post("/login", data={"email": "teacher@ecoquest.test", "password": "Teacher@123"})
    r2 = t.get("/teacher/students.csv")
    assert r2.mimetype == "text/csv" and b"Anurag Student" in r2.data
    assert student.get("/teacher/students.csv").status_code == 302           # students cannot export class data


def test_announcements(teacher, app, db):                                   # TC-72
    teacher.post("/teacher/announcements", data={"title": "TEST Plastic-Free Week", "message": "Starts Monday!"})
    s = app.test_client()
    s.post("/login", data={"email": "student@ecoquest.test", "password": "Student@123"})
    assert b"TEST Plastic-Free Week" in s.get("/student/dashboard").data
    aid = one(db, "SELECT announcement_id FROM announcements WHERE title='TEST Plastic-Free Week'")["announcement_id"]
    teacher.post(f"/teacher/announcements/{aid}/delete")
    assert one(db, "SELECT COUNT(*) AS n FROM announcements WHERE announcement_id=%s", (aid,))["n"] == 0


@pytest.mark.parametrize("key", ["myth-buster", "renewable-sort", "water-wise"])
def test_new_games_playable(student, db, key):                              # TC-73
    assert student.get(f"/games/{key}").status_code == 200
    with student.session_transaction() as s:
        ids = s[f"game_{key}"]
    lookup = {i[0]: i[3] for i in GAMES[key]["items"]}
    r = student.post(f"/games/{key}/finish", data={f"ans_{i}": lookup[i] for i in ids})
    assert r.status_code == 200 and f"{len(ids)}/{len(ids)}".encode() in r.data


def test_new_badge_rules(db):                                               # TC-74
    uid = user_id(db)
    with db.cursor() as cur:
        for _ in range(5):
            cur.execute("INSERT INTO activity_log (user_id, activity, description, xp_change) VALUES (%s,'pulse','t',5)", (uid,))
    names = [b["name"] for b in g.check_badges(db, uid)]
    assert "Air Watcher" in names
    db.commit()


def test_activity_calendar_and_pages(student, db):                          # TC-75
    cal = g.activity_calendar(db, user_id(db))
    assert len(cal) == 28 and not any(d["active"] for d in cal)
    for url in ("/student/progress", "/account/password", "/student/dashboard"):
        assert student.get(url).status_code == 200
