"""Create the EcoQuest tables and load demo data.

Usage:
    python init_db.py            # create tables and load the environmental content (no fake users)
    python init_db.py --demo     # also create fictional demo accounts and sample classmate activity
    python init_db.py --reset    # DROP all tables first (development only!)
"""
import os
import sys
from datetime import date, timedelta

import pymysql

import config
from database import extra_content, seed_data
from utils.auth import hash_password
from utils.database import connect, execute, fetch_one
from utils.gamification import check_badges, add_xp

HERE = os.path.dirname(os.path.abspath(__file__))
TABLES = ["announcements", "air_readings", "activity_log", "user_progress", "user_badges", "badges", "challenge_completions",
          "challenges", "quiz_answers", "quiz_attempts", "options", "questions", "quizzes",
          "lessons", "topics", "users", "roles"]


def run_schema(conn):
    with open(os.path.join(HERE, "database", "schema.sql"), encoding="utf-8") as f:
        statements = [s.strip() for s in f.read().split(";") if s.strip()]
    for stmt in statements:
        execute(conn, stmt)
    conn.commit()


def drop_all(conn):
    execute(conn, "SET FOREIGN_KEY_CHECKS = 0")
    for table in TABLES:
        execute(conn, f"DROP TABLE IF EXISTS {table}")
    execute(conn, "SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()


def seed_content(conn):
    for role in ("student", "teacher", "admin"):
        execute(conn, "INSERT INTO roles (role_name) VALUES (%s)", (role,))
    topic_ids = {}
    for name, icon, desc in seed_data.TOPICS:
        topic_ids[name] = execute(conn, "INSERT INTO topics (name, icon, description) VALUES (%s,%s,%s)",
                                  (name, icon, desc))
    for topic, title, diff, intro, expl, points, tip in seed_data.LESSONS:
        execute(conn,
                "INSERT INTO lessons (topic_id, title, difficulty, introduction, explanation, key_points, eco_tip) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (topic_ids[topic], title, diff, intro, expl, "\n".join(points), tip))
    for topic, title, desc, questions in seed_data.QUIZZES:
        quiz_id = execute(conn, "INSERT INTO quizzes (topic_id, title, description) VALUES (%s,%s,%s)",
                          (topic_ids[topic], title, desc))
        for text, opts, correct, why in questions:
            qid = execute(conn, "INSERT INTO questions (quiz_id, question_text, explanation) VALUES (%s,%s,%s)",
                          (quiz_id, text, why))
            for i, opt in enumerate(opts):
                execute(conn, "INSERT INTO options (question_id, option_text, is_correct) VALUES (%s,%s,%s)",
                        (qid, opt, 1 if i == correct else 0))
    for topic, title, desc, diff, xp in seed_data.CHALLENGES:
        execute(conn,
                "INSERT INTO challenges (topic_id, title, description, difficulty, xp_reward) VALUES (%s,%s,%s,%s,%s)",
                (topic_ids[topic], title, desc, diff, xp))
    for name, desc, icon, rule, value, topic in seed_data.BADGES:
        execute(conn,
                "INSERT INTO badges (name, description, icon, rule_type, rule_value, topic_id) VALUES (%s,%s,%s,%s,%s,%s)",
                (name, desc, icon, rule, value, topic_ids.get(topic)))
    conn.commit()


def upgrade_schema(conn):
    """Add columns introduced after the first release (safe to repeat)."""
    has = fetch_one(conn, "SELECT COUNT(*) AS n FROM information_schema.columns WHERE table_schema = DATABASE() "
                          "AND table_name = 'quizzes' AND column_name = 'difficulty'")
    if not has["n"]:
        execute(conn, "ALTER TABLE quizzes ADD COLUMN difficulty ENUM('Beginner','Intermediate','Advanced') "
                      "NOT NULL DEFAULT 'Beginner' AFTER description")
        conn.commit()


def ensure_extra_content(conn):
    """Add the extra levels of content (matched by title, safe to repeat)."""
    tid = lambda name: fetch_one(conn, "SELECT topic_id FROM topics WHERE name = %s", (name,))["topic_id"]
    for topic, title, diff, intro, expl, points, tip in extra_content.LESSONS:
        if not fetch_one(conn, "SELECT 1 AS x FROM lessons WHERE title = %s", (title,)):
            execute(conn, "INSERT INTO lessons (topic_id, title, difficulty, introduction, explanation, key_points, eco_tip) "
                          "VALUES (%s,%s,%s,%s,%s,%s,%s)", (tid(topic), title, diff, intro, expl, "\n".join(points), tip))
    for topic, title, desc, diff, questions in extra_content.QUIZZES:
        if fetch_one(conn, "SELECT 1 AS x FROM quizzes WHERE title = %s", (title,)):
            continue
        quiz_id = execute(conn, "INSERT INTO quizzes (topic_id, title, description, difficulty) VALUES (%s,%s,%s,%s)",
                          (tid(topic), title, desc, diff))
        for text, opts, correct, why in questions:
            qid = execute(conn, "INSERT INTO questions (quiz_id, question_text, explanation) VALUES (%s,%s,%s)", (quiz_id, text, why))
            for i, opt in enumerate(opts):
                execute(conn, "INSERT INTO options (question_id, option_text, is_correct) VALUES (%s,%s,%s)",
                        (qid, opt, 1 if i == correct else 0))
    for topic, title, desc, diff, xp in extra_content.CHALLENGES:
        if not fetch_one(conn, "SELECT 1 AS x FROM challenges WHERE title = %s", (title,)):
            execute(conn, "INSERT INTO challenges (topic_id, title, description, difficulty, xp_reward) VALUES (%s,%s,%s,%s,%s)",
                    (tid(topic), title, desc, diff, xp))
    conn.commit()


def ensure_badges(conn):
    """Add badges that were introduced after the first release (matched by name, safe to repeat)."""
    for name, desc, icon, rule, value, topic in seed_data.BADGES:
        if not fetch_one(conn, "SELECT 1 AS x FROM badges WHERE name = %s", (name,)):
            t = fetch_one(conn, "SELECT topic_id FROM topics WHERE name = %s", (topic,)) if topic else None
            execute(conn, "INSERT INTO badges (name, description, icon, rule_type, rule_value, topic_id) VALUES (%s,%s,%s,%s,%s,%s)",
                    (name, desc, icon, rule, value, t["topic_id"] if t else None))
    conn.commit()


def seed_users(conn):
    """Demo accounts. Passwords are hashed with Werkzeug before storing."""
    for name, email, password, role, inst, cls in seed_data.DEMO_USERS:
        role_id = fetch_one(conn, "SELECT role_id FROM roles WHERE role_name = %s", (role,))["role_id"]
        execute(conn,
                "INSERT INTO users (name, email, password_hash, role_id, institution, class_name) "
                "VALUES (%s,%s,%s,%s,%s,%s)",
                (name, email, hash_password(password), role_id, inst, cls))
    conn.commit()


def seed_sample_activity(conn):
    """Give some classmates realistic activity so the leaderboard and teacher charts have data."""
    today = date.today()
    plans = {"riya@ecoquest.test": (6, 2, 4, 5), "kabir@ecoquest.test": (3, 1, 2, 3), "sara@ecoquest.test": (2, 1, 1, 1)}
    quizzes = [r["quiz_id"] for r in _all(conn, "SELECT quiz_id FROM quizzes ORDER BY quiz_id")]
    for email, (n_lessons, n_quizzes, n_challenges, streak) in plans.items():
        uid = fetch_one(conn, "SELECT user_id FROM users WHERE email = %s", (email,))["user_id"]
        lessons = _all(conn, "SELECT lesson_id, title FROM lessons ORDER BY lesson_id LIMIT %s", (n_lessons,))
        for les in lessons:
            execute(conn, "INSERT INTO user_progress (user_id, lesson_id) VALUES (%s,%s)", (uid, les["lesson_id"]))
            add_xp(conn, uid, 10, "lesson", f"Completed lesson: {les['title']}")
        for qid in quizzes[:n_quizzes]:
            total = fetch_one(conn, "SELECT COUNT(*) AS n FROM questions WHERE quiz_id = %s", (qid,))["n"]
            score = total - 1
            xp = score * 10
            execute(conn, "INSERT INTO quiz_attempts (user_id, quiz_id, score, total_questions, xp_earned) "
                          "VALUES (%s,%s,%s,%s,%s)", (uid, qid, score, total, xp))
            add_xp(conn, uid, xp, "quiz", "Completed a quiz")
        chs = _all(conn, "SELECT challenge_id, title, xp_reward FROM challenges ORDER BY challenge_id LIMIT %s",
                   (n_challenges,))
        for i, ch in enumerate(chs):
            execute(conn, "INSERT INTO challenge_completions (user_id, challenge_id, completed_on, xp_earned) "
                          "VALUES (%s,%s,%s,%s)", (uid, ch["challenge_id"], today - timedelta(days=i % 3), ch["xp_reward"]))
            add_xp(conn, uid, ch["xp_reward"], "challenge", f"Completed challenge: {ch['title']}")
        execute(conn, "UPDATE users SET streak = %s, last_active = %s WHERE user_id = %s", (streak, today, uid))
        check_badges(conn, uid)
    conn.commit()


def _all(conn, sql, args=None):
    with conn.cursor() as cur:
        cur.execute(sql, args or ())
        return cur.fetchall()


def ensure_database():
    """Create the database itself if the MySQL user is allowed to (ignored on managed hosts)."""
    try:
        conn = pymysql.connect(host=config.DB_HOST, port=config.DB_PORT, user=config.DB_USER,
                               password=config.DB_PASSWORD)
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}` CHARACTER SET utf8mb4")
        conn.close()
    except pymysql.MySQLError:
        pass


def init(reset=False, demo_users=False, with_sample_activity=False):
    """Create tables, load content. Demo accounts/activity only when asked (--demo)."""
    ensure_database()
    conn = connect()
    try:
        if reset:
            drop_all(conn)
        run_schema(conn)
        if fetch_one(conn, "SELECT COUNT(*) AS n FROM roles")["n"] == 0:
            seed_content(conn)
            print("Environmental content loaded.")
        upgrade_schema(conn)
        ensure_extra_content(conn)
        ensure_badges(conn)
        if demo_users and fetch_one(conn, "SELECT COUNT(*) AS n FROM users")["n"] == 0:
            seed_users(conn)
            print("Demo accounts created (fictional; see docs/user_manual.md).")
            if with_sample_activity:
                seed_sample_activity(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    demo = "--demo" in sys.argv
    init(reset="--reset" in sys.argv, demo_users=demo, with_sample_activity=demo)
    sys.exit(0)
