"""EcoQuest configuration. All secrets come from environment variables (.env)."""
import os
import secrets

from dotenv import load_dotenv

load_dotenv()


def _env(*names, default=None):
    """Return the first environment variable that is set (supports Railway's MYSQL* names)."""
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return default


# ---- Database -------------------------------------------------------------
DB_HOST = _env("DB_HOST", "MYSQLHOST", default="127.0.0.1")
DB_PORT = int(_env("DB_PORT", "MYSQLPORT", default="3306"))
DB_USER = _env("DB_USER", "MYSQLUSER", default="root")
DB_PASSWORD = _env("DB_PASSWORD", "MYSQLPASSWORD", default="")
DB_NAME = _env("DB_NAME", "MYSQLDATABASE", default="ecoquest")

# ---- Flask ----------------------------------------------------------------
# In production SECRET_KEY must be set; otherwise a random key is generated
# for this run only (sessions are lost on restart).
SECRET_KEY = _env("SECRET_KEY", default=None) or secrets.token_hex(32)
DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"

# ---- Gamification rules (configurable) --------------------------------------
XP_LESSON = 10             # lesson completed
XP_CORRECT_ANSWER = 10     # each correct quiz answer
XP_PERFECT_QUIZ_BONUS = 50
XP_STREAK_BONUS = 100      # awarded every time the streak reaches a multiple of 7
STREAK_BONUS_DAYS = 7
XP_PER_LEVEL = 100         # level = XP // 100 + 1
XP_GAME_PER_CORRECT = 5    # mini-games: per correct answer (+ perfect bonus below)
XP_GAME_PERFECT_BONUS = 10
XP_DAILY_QUEST_BONUS = 25  # bonus for finishing all four daily quests
WEEKLY_GOAL_XP = 200       # XP to earn in a week (Mon-Sun) ...
XP_WEEKLY_BONUS = 50       # ... for this one-time weekly bonus
XP_PULSE_CORRECT = 15      # Eco Pulse daily prediction: correct
XP_PULSE_TRY = 5           # Eco Pulse daily prediction: wrong (still rewarded for checking in)
