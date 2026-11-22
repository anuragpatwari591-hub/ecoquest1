# Developer Guide

## Project layout
```
app.py                 Flask app factory, CSRF check, error pages, landing route
config.py              Environment-based configuration and XP rules
init_db.py             Creates tables from schema.sql and loads demo data
database/schema.sql    MySQL schema (15 tables)
database/seed_data.py  Topics, lessons, quizzes, challenges, badges, demo users
routes/                One Flask Blueprint per area: auth, student, quiz, challenge, teacher, admin
utils/database.py      Connection per request + fetch_all/fetch_one/execute helpers
utils/auth.py          Hashing, authenticate(), @login_required(role)
utils/gamification.py  Level, XP, streak, badges, progress, leaderboard
templates/ static/     Jinja2 templates, CSS, JavaScript
tests/                 pytest suite (uses the ecoquest_test database)
docs/                  Documentation
```

## How the code fits together
* `create_app()` registers all blueprints and a `before_request` CSRF check.
* A route gets the DB connection with `get_db()` (stored in Flask's `g`, closed automatically after the request).
* Business rules are in `utils/gamification.py`. Functions take a connection and **do not commit**; the route commits once the whole action succeeds.
* `record_activity(conn, user_id, xp, activity, description)` is the single entry point used after a lesson, quiz or challenge: it adds XP, updates the streak (with bonus) and checks badges.

## Key algorithms (short)
```python
level = xp // 100 + 1                                   # calculate_level
quiz_xp = score * 10 + (50 if score == total else 0)    # calculate_quiz_xp
# streak
if last_active is None:              streak = 1
elif last_active == today:           streak unchanged
elif last_active == today - 1 day:   streak += 1
else:                                streak = 1
# badge check: for each badge the user does not own, compute the user's value for badge.rule_type
# and insert into user_badges when value >= badge.rule_value
```
Leaderboard is a SQL query with `ORDER BY total_xp DESC`; rank = position in that result.

## Configuration of XP rules
`config.py`: `XP_LESSON`, `XP_CORRECT_ANSWER`, `XP_PERFECT_QUIZ_BONUS`, `XP_STREAK_BONUS`, `STREAK_BONUS_DAYS`, `XP_PER_LEVEL`.

## Adding a new badge rule type
1. Add a branch in `_badge_progress_value()` returning the user's current value.
2. Add the rule name to `BADGE_RULES` in `routes/admin.py`.

## Running tests
```powershell
python -m pytest -v
```
Tests use the database named `ecoquest_test` (the DB user needs privileges on it). The suite recreates it at start.

## Conventions
* Always use `%s` placeholders — never build SQL with f-strings from user input.
* Every POST form must include `<input type="hidden" name="csrf_token" value="{{ csrf_token }}">`.
* Protect every new route with `@login_required("role")`.
