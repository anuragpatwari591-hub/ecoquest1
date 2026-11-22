"""EcoQuest gamification logic: XP, levels, streaks, badges, progress.

Functions take a database connection and never commit; the calling route
commits once the whole action (e.g. completing a lesson) succeeded.
"""
from datetime import date, timedelta

import config
from utils.database import execute, fetch_all, fetch_one


# ---------------------------------------------------------------- levels
def calculate_level(xp):
    """Level = floor(XP / 100) + 1."""
    return xp // config.XP_PER_LEVEL + 1


def level_info(xp):
    """Return level, XP inside the level, XP needed for next level and progress %."""
    level = calculate_level(xp)
    into_level = xp % config.XP_PER_LEVEL
    return {
        "level": level,
        "xp": xp,
        "xp_into_level": into_level,
        "xp_to_next": config.XP_PER_LEVEL - into_level,
        "percent": int(into_level * 100 / config.XP_PER_LEVEL),
    }


# ---------------------------------------------------------------- quiz scoring
def calculate_quiz_xp(score, total):
    """10 XP per correct answer, plus a 50 XP bonus for a perfect score."""
    xp = score * config.XP_CORRECT_ANSWER
    if total > 0 and score == total:
        xp += config.XP_PERFECT_QUIZ_BONUS
    return xp


def calculate_accuracy(score, total):
    return round(score * 100 / total) if total else 0


# ---------------------------------------------------------------- streak
def next_streak(last_active, current_streak, today=None):
    """Pure streak rule.

    * first activity ever            -> streak 1
    * already active today           -> unchanged
    * last active yesterday          -> streak + 1
    * missed one or more days        -> reset to 1
    """
    today = today or date.today()
    if last_active is None:
        return 1
    if last_active == today:
        return max(current_streak, 1)
    if last_active == today - timedelta(days=1):
        return current_streak + 1
    return 1


def update_streak(conn, user_id, today=None):
    """Update the user's streak for today's activity. Returns bonus XP awarded (0 or 100)."""
    today = today or date.today()
    user = fetch_one(conn, "SELECT streak, last_active FROM users WHERE user_id = %s", (user_id,))
    if user["last_active"] == today:
        return 0                               # already counted today
    new_streak = next_streak(user["last_active"], user["streak"], today)
    execute(conn, "UPDATE users SET streak = %s, last_active = %s WHERE user_id = %s",
            (new_streak, today, user_id))
    if new_streak % config.STREAK_BONUS_DAYS == 0:
        add_xp(conn, user_id, config.XP_STREAK_BONUS, "streak",
               f"{new_streak}-day streak bonus")
        return config.XP_STREAK_BONUS
    return 0


# ---------------------------------------------------------------- XP
def add_xp(conn, user_id, amount, activity, description):
    """Add XP to the user's total and write an activity-log row."""
    execute(conn, "UPDATE users SET total_xp = total_xp + %s WHERE user_id = %s", (amount, user_id))
    execute(conn,
            "INSERT INTO activity_log (user_id, activity, description, xp_change) VALUES (%s,%s,%s,%s)",
            (user_id, activity, description, amount))


def record_activity(conn, user_id, amount, activity, description, today=None):
    """Award XP for an eligible activity, update the streak, daily quests and badges.

    Returns a dict: {'xp': total XP gained (incl. bonuses), 'bonus': streak bonus,
    'quest_bonus': daily-quest bonus, 'level_up': new level or None, 'badges': [new badge rows]}
    """
    old_level = calculate_level(fetch_one(conn, "SELECT total_xp FROM users WHERE user_id = %s", (user_id,))["total_xp"])
    add_xp(conn, user_id, amount, activity, description)
    bonus = update_streak(conn, user_id, today)
    quest_bonus = 0
    if activity in QUEST_ACTIVITIES and daily_quests(conn, user_id)["all_done"] and not fetch_one(
            conn, "SELECT 1 AS x FROM activity_log WHERE user_id = %s AND activity = 'quest' "
                  "AND DATE(created_at) = CURDATE()", (user_id,)):
        quest_bonus = config.XP_DAILY_QUEST_BONUS
        add_xp(conn, user_id, quest_bonus, "quest", "Daily quests complete bonus")
    new_badges = check_badges(conn, user_id)
    new_level = calculate_level(fetch_one(conn, "SELECT total_xp FROM users WHERE user_id = %s", (user_id,))["total_xp"])
    return {"xp": amount + bonus + quest_bonus, "bonus": bonus, "quest_bonus": quest_bonus,
            "level_up": new_level if new_level > old_level else None, "badges": new_badges}


# ---------------------------------------------------------------- daily quests
QUEST_ACTIVITIES = ("lesson", "quiz", "challenge", "game")
QUEST_LABELS = {"lesson": ("📖", "Complete a lesson"), "quiz": ("🧠", "Take a quiz"),
                "challenge": ("🌿", "Do an eco challenge"), "game": ("🎮", "Play a mini-game")}


def daily_quests(conn, user_id):
    """Four simple quests; each is done when the student has that kind of activity today."""
    rows = fetch_all(conn, "SELECT DISTINCT activity FROM activity_log WHERE user_id = %s "
                           "AND DATE(created_at) = CURDATE()", (user_id,))
    done_today = {r["activity"] for r in rows}
    quests = [{"key": k, "icon": QUEST_LABELS[k][0], "label": QUEST_LABELS[k][1], "done": k in done_today}
              for k in QUEST_ACTIVITIES]
    return {"quests": quests, "done": sum(q["done"] for q in quests), "all_done": all(q["done"] for q in quests),
            "bonus": config.XP_DAILY_QUEST_BONUS}


# ---------------------------------------------------------------- Eco City
def city_stage(level):
    """The student's Eco City gets cleaner as the level rises (pollution 95% at level 1 ... 5% at level 10+)."""
    pollution = max(5, 95 - (level - 1) * 10)
    if level < 3:
        name, scene = "Smoggy Town", "🏭 🌫️ 🏚️ 🚗 💨"
    elif level < 5:
        name, scene = "Awakening Town", "🏘️ 🌱 🚌 🏭 🌤️"
    elif level < 8:
        name, scene = "Green Neighbourhood", "🏡 🌳 🚲 ☀️ 🌻"
    else:
        name, scene = "Eco City", "🏙️ 🌳 🚋 ☀️ 🦋 🌈"
    air = "Poor" if pollution > 70 else "Moderate" if pollution > 40 else "Good" if pollution > 20 else "Excellent"
    return {"name": name, "scene": scene, "pollution": pollution, "air": air}


# ---------------------------------------------------------------- badges
def _badge_progress_value(conn, user_id, badge):
    """Return the user's current value for this badge's rule type."""
    rule, topic = badge["rule_type"], badge["topic_id"]
    if rule == "lessons":
        sql, args = "SELECT COUNT(*) AS n FROM user_progress WHERE user_id = %s", (user_id,)
    elif rule == "quizzes":
        sql, args = "SELECT COUNT(*) AS n FROM quiz_attempts WHERE user_id = %s", (user_id,)
    elif rule == "topic_challenges":
        sql = ("SELECT COUNT(*) AS n FROM challenge_completions cc "
               "JOIN challenges c ON cc.challenge_id = c.challenge_id "
               "WHERE cc.user_id = %s AND c.topic_id = %s")
        args = (user_id, topic)
    elif rule == "topic_activity":      # lessons + challenges in a topic
        sql = ("SELECT (SELECT COUNT(*) FROM user_progress up JOIN lessons l ON up.lesson_id = l.lesson_id "
               "        WHERE up.user_id = %s AND l.topic_id = %s) + "
               "       (SELECT COUNT(*) FROM challenge_completions cc JOIN challenges c "
               "        ON cc.challenge_id = c.challenge_id WHERE cc.user_id = %s AND c.topic_id = %s) AS n")
        args = (user_id, topic, user_id, topic)
    elif rule == "streak":
        sql, args = "SELECT streak AS n FROM users WHERE user_id = %s", (user_id,)
    elif rule == "games":
        sql, args = "SELECT COUNT(*) AS n FROM activity_log WHERE user_id = %s AND activity = 'game'", (user_id,)
    elif rule == "xp":
        sql, args = "SELECT total_xp AS n FROM users WHERE user_id = %s", (user_id,)
    else:
        return 0
    return fetch_one(conn, sql, args)["n"]


def badge_is_earned(current_value, required_value):
    return current_value >= required_value


def check_badges(conn, user_id):
    """Award every badge whose rule is now satisfied. Returns the list of newly earned badges."""
    unearned = fetch_all(
        conn,
        "SELECT * FROM badges WHERE badge_id NOT IN "
        "(SELECT badge_id FROM user_badges WHERE user_id = %s)", (user_id,))
    earned_now = []
    for badge in unearned:
        value = _badge_progress_value(conn, user_id, badge)
        if badge_is_earned(value, badge["rule_value"]):
            execute(conn, "INSERT IGNORE INTO user_badges (user_id, badge_id) VALUES (%s,%s)",
                    (user_id, badge["badge_id"]))
            execute(conn,
                    "INSERT INTO activity_log (user_id, activity, description, xp_change) "
                    "VALUES (%s,'badge',%s,0)", (user_id, f"Earned badge: {badge['name']}"))
            earned_now.append(badge)
    return earned_now


# ---------------------------------------------------------------- progress
def topic_progress(conn, user_id):
    """Per-topic progress % = (completed lessons + completed distinct challenges + quizzes taken)
    divided by (lessons + challenges + quizzes) available in that topic."""
    return fetch_all(conn, """
        SELECT t.topic_id, t.name, t.icon,
               (SELECT COUNT(*) FROM lessons l WHERE l.topic_id = t.topic_id) AS lessons_total,
               (SELECT COUNT(*) FROM user_progress up JOIN lessons l ON up.lesson_id = l.lesson_id
                 WHERE up.user_id = %s AND l.topic_id = t.topic_id) AS lessons_done,
               (SELECT COUNT(*) FROM quizzes q WHERE q.topic_id = t.topic_id) AS quizzes_total,
               (SELECT COUNT(DISTINCT qa.quiz_id) FROM quiz_attempts qa JOIN quizzes q ON qa.quiz_id = q.quiz_id
                 WHERE qa.user_id = %s AND q.topic_id = t.topic_id) AS quizzes_done,
               (SELECT COUNT(*) FROM challenges c WHERE c.topic_id = t.topic_id AND c.is_active = 1) AS challenges_total,
               (SELECT COUNT(DISTINCT cc.challenge_id) FROM challenge_completions cc
                 JOIN challenges c ON cc.challenge_id = c.challenge_id
                 WHERE cc.user_id = %s AND c.topic_id = t.topic_id) AS challenges_done
        FROM topics t ORDER BY t.topic_id""", (user_id, user_id, user_id))


def progress_percent(row):
    total = row["lessons_total"] + row["quizzes_total"] + row["challenges_total"]
    done = min(row["lessons_done"], row["lessons_total"]) + row["quizzes_done"] + min(
        row["challenges_done"], row["challenges_total"])
    return int(done * 100 / total) if total else 0


def topic_progress_list(conn, user_id):
    rows = topic_progress(conn, user_id)
    for r in rows:
        r["percent"] = progress_percent(r)
    return rows


# ---------------------------------------------------------------- leaderboard
def leaderboard(conn, institution=None, class_name=None, limit=50):
    """Students ranked by XP using SQL ORDER BY (optionally filtered)."""
    sql = ("SELECT u.user_id, u.name, u.institution, u.class_name, u.total_xp, "
           "(SELECT COUNT(*) FROM user_badges ub WHERE ub.user_id = u.user_id) AS badge_count "
           "FROM users u JOIN roles r ON u.role_id = r.role_id "
           "WHERE r.role_name = 'student' AND u.is_active = 1")
    args = []
    if institution:
        sql += " AND u.institution = %s"
        args.append(institution)
    if class_name:
        sql += " AND u.class_name = %s"
        args.append(class_name)
    sql += " ORDER BY u.total_xp DESC, u.name ASC LIMIT %s"
    args.append(limit)
    rows = fetch_all(conn, sql, args)
    for i, row in enumerate(rows, start=1):
        row["rank"] = i
        row["level"] = calculate_level(row["total_xp"])
    return rows


def student_rank(conn, user_id):
    """Rank = 1 + number of active students with strictly more XP."""
    me = fetch_one(conn, "SELECT total_xp FROM users WHERE user_id = %s", (user_id,))
    row = fetch_one(conn,
                    "SELECT COUNT(*) + 1 AS rnk FROM users u JOIN roles r ON u.role_id = r.role_id "
                    "WHERE r.role_name = 'student' AND u.is_active = 1 AND u.total_xp > %s",
                    (me["total_xp"],))
    return row["rnk"]
