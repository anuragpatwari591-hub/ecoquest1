# EcoQuest — Coding Viva

Every solution uses only the project's technologies (Python, Flask, PyMySQL, MySQL).

## 1. Write a Flask route
**Q.** Write a route `/hello/<name>` that shows a greeting.
```python
from flask import Flask
app = Flask(__name__)

@app.route("/hello/<name>")
def hello(name):
    return f"Hello, {name}!"
```
**Explanation:** `@app.route` maps the URL to the function; `<name>` is passed as an argument. Output for `/hello/Anurag`: `Hello, Anurag!`

## 2. Connect Python to MySQL
```python
import pymysql
conn = pymysql.connect(host="127.0.0.1", user="ecoquest", password="***", database="ecoquest",
                       cursorclass=pymysql.cursors.DictCursor)
```
**Explanation:** `connect` opens a connection; `DictCursor` returns rows as dictionaries. In the project this is `utils/database.py → connect()`, reading values from environment variables (never hard-coded).

## 3. Insert a user
```python
with conn.cursor() as cur:
    cur.execute("INSERT INTO users (name, email, password_hash, role_id) VALUES (%s,%s,%s,%s)",
                ("Asha", "asha@example.com", generate_password_hash("secret1"), 1))
conn.commit()
```
**Explanation:** `%s` placeholders prevent SQL injection; `commit()` saves the change. The password is hashed.

## 4. Retrieve a user
```python
with conn.cursor() as cur:
    cur.execute("SELECT user_id, name FROM users WHERE email = %s", ("asha@example.com",))
    user = cur.fetchone()      # {'user_id': 7, 'name': 'Asha'} or None
```

## 5. Write a SELECT query (lessons of a topic)
```sql
SELECT lesson_id, title, difficulty FROM lessons WHERE topic_id = 1 ORDER BY lesson_id;
```

## 6. Write a JOIN (quiz with topic name and question count)
```sql
SELECT q.title, t.name AS topic, COUNT(qs.question_id) AS questions
FROM quizzes q
JOIN topics t ON q.topic_id = t.topic_id
LEFT JOIN questions qs ON qs.quiz_id = q.quiz_id
GROUP BY q.quiz_id, q.title, t.name;
```
**Explanation:** JOIN links tables via keys; LEFT JOIN keeps quizzes with no questions; GROUP BY + COUNT aggregates.

## 7. Calculate quiz score
```python
def calculate_score(correct_flags):
    return sum(1 for c in correct_flags if c)

print(calculate_score([1, 0, 1, 1, 0]))   # 3
```
In the project, `grade()` compares each selected option with `options.is_correct` on the server.

## 8. Calculate quiz XP
```python
def calculate_quiz_xp(score, total):
    xp = score * 10
    if score == total:
        xp += 50          # perfect bonus
    return xp

print(calculate_quiz_xp(8, 10))   # 80
print(calculate_quiz_xp(10, 10))  # 150
```

## 9. Calculate level
```python
def calculate_level(xp):
    return xp // 100 + 1

print(calculate_level(0), calculate_level(99), calculate_level(250))   # 1 1 3
```

## 10. Check badge eligibility
```python
def badge_is_earned(current_value, required_value):
    return current_value >= required_value

lessons_done = 1
print(badge_is_earned(lessons_done, 1))   # True -> award "Green Beginner"
```
SQL version for "Eco Learner" (5 quizzes): `SELECT COUNT(*) FROM quiz_attempts WHERE user_id = %s` then compare with 5.

## 11. Leaderboard query
```sql
SELECT u.name, u.total_xp
FROM users u JOIN roles r ON u.role_id = r.role_id
WHERE r.role_name = 'student'
ORDER BY u.total_xp DESC;
```
Rank = row position (1, 2, 3…).

## 12. Login validation
```python
from werkzeug.security import check_password_hash

def authenticate(conn, email, password):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE email = %s", (email.lower(),))
        user = cur.fetchone()
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None
```
**Explanation:** look up by email, then compare the typed password with the stored hash (the original password is never stored).

## 13. Session-based authorization
```python
from functools import wraps
from flask import session, redirect, url_for

def login_required(role):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if session.get("role") != role:
                return redirect(url_for("auth.login"))
            return view(*args, **kwargs)
        return wrapper
    return decorator

@app.route("/admin")
@login_required("admin")
def admin_home(): ...
```

## 14. Calculate topic progress
```python
def progress_percent(done, total):
    return int(done * 100 / total) if total else 0

print(progress_percent(2, 4))   # 50
```
Project version: (lessons done + quizzes done + challenges done) ÷ (lessons + quizzes + challenges) × 100.

## 15. Prevent duplicate challenge completion
```sql
ALTER TABLE challenge_completions
  ADD UNIQUE KEY uq_user_challenge_day (user_id, challenge_id, completed_on);
```
```python
cur.execute("SELECT 1 FROM challenge_completions WHERE user_id=%s AND challenge_id=%s AND completed_on=%s",
            (uid, cid, today))
if cur.fetchone():
    return "Already completed today"
```
**Explanation:** the code check gives a friendly message; the UNIQUE key guarantees integrity even if two requests arrive together.

## 16. Streak calculation
```python
from datetime import date, timedelta

def next_streak(last_active, streak, today):
    if last_active is None:
        return 1
    if last_active == today:
        return streak
    if last_active == today - timedelta(days=1):
        return streak + 1
    return 1

print(next_streak(date(2026, 5, 9), 4, date(2026, 5, 10)))   # 5
print(next_streak(date(2026, 5, 7), 4, date(2026, 5, 10)))   # 1
```

## 17. Average score per quiz
```sql
SELECT q.title, ROUND(AVG(a.score * 100 / a.total_questions)) AS avg_pct
FROM quizzes q JOIN quiz_attempts a ON q.quiz_id = a.quiz_id
GROUP BY q.quiz_id, q.title;
```

## 18. Create a table with keys
```sql
CREATE TABLE user_badges (
  user_id INT NOT NULL, badge_id INT NOT NULL,
  earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, badge_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (badge_id) REFERENCES badges(badge_id) ON DELETE CASCADE
);
```
