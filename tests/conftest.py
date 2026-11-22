"""Shared test fixtures. Tests run against a separate MySQL database: ecoquest_test."""
import os
import sys

# Must be set BEFORE config is imported, so the app talks to the test database.
os.environ["DB_NAME"] = "ecoquest_test"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

import init_db  # noqa: E402
from app import create_app  # noqa: E402
from utils.database import connect  # noqa: E402

DEMO = {
    "student": ("student@ecoquest.test", "Student@123"),
    "teacher": ("teacher@ecoquest.test", "Teacher@123"),
    "admin": ("admin@ecoquest.test", "Admin@123"),
}


@pytest.fixture(scope="session", autouse=True)
def _database():
    init_db.init(reset=True, with_sample_activity=False)


@pytest.fixture(autouse=True)
def clean_state():
    """Before every test: remove user-generated rows and reset demo users."""
    conn = connect()
    with conn.cursor() as cur:
        for table in ("activity_log", "user_badges", "user_progress", "quiz_answers",
                      "quiz_attempts", "challenge_completions"):
            cur.execute(f"DELETE FROM {table}")
        cur.execute("DELETE FROM users WHERE email NOT LIKE '%@ecoquest.test'")
        cur.execute("UPDATE users SET total_xp = 0, streak = 0, last_active = NULL, is_active = 1")
        cur.execute("DELETE FROM quizzes WHERE title LIKE 'TEST %'")
        cur.execute("DELETE FROM challenges WHERE title LIKE 'TEST %'")
    conn.commit()
    conn.close()
    yield


@pytest.fixture()
def app():
    return create_app(testing=True)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db():
    conn = connect()
    yield conn
    conn.close()


def login(client, role):
    email, password = DEMO[role]
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=False)


@pytest.fixture()
def student(client):
    login(client, "student")
    return client


@pytest.fixture()
def teacher(client):
    login(client, "teacher")
    return client


@pytest.fixture()
def admin(client):
    login(client, "admin")
    return client


def user_id(db, email="student@ecoquest.test"):
    with db.cursor() as cur:
        cur.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        return cur.fetchone()["user_id"]


def one(db, sql, args=None):
    db.commit()                      # make sure we see the latest committed data
    with db.cursor() as cur:
        cur.execute(sql, args or ())
        return cur.fetchone()
