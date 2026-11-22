"""Student challenges: list and complete."""
from datetime import date

import pymysql
from flask import Blueprint, abort, flash, redirect, render_template, session, url_for

from utils.auth import login_required
from utils.database import execute, fetch_all, fetch_one, get_db
from utils.gamification import record_activity
from utils.ui import flash_rewards

challenge_bp = Blueprint("challenge", __name__, url_prefix="/challenges")


def complete_challenge(db, user_id, challenge_id, today=None):
    """Record a challenge completion and award XP.

    A challenge can be completed once per day (UNIQUE key in the database).
    Returns the result dict from record_activity, or None if already completed today.
    """
    today = today or date.today()
    ch = fetch_one(db, "SELECT * FROM challenges WHERE challenge_id = %s AND is_active = 1", (challenge_id,))
    if not ch:
        raise LookupError("challenge not found")
    if fetch_one(db, "SELECT 1 AS x FROM challenge_completions WHERE user_id = %s AND challenge_id = %s "
                     "AND completed_on = %s", (user_id, challenge_id, today)):
        return None
    try:
        execute(db, "INSERT INTO challenge_completions (user_id, challenge_id, completed_on, xp_earned) "
                    "VALUES (%s,%s,%s,%s)", (user_id, challenge_id, today, ch["xp_reward"]))
    except pymysql.IntegrityError:          # double click / race: the UNIQUE key blocks the duplicate
        return None
    return record_activity(db, user_id, ch["xp_reward"], "challenge",
                           f"Completed challenge: {ch['title']}", today)


@challenge_bp.route("/")
@login_required("student")
def challenge_list():
    db, uid = get_db(), session["user_id"]
    rows = fetch_all(db, "SELECT c.*, t.name AS topic_name, t.icon, "
                         "(SELECT COUNT(*) FROM challenge_completions cc WHERE cc.challenge_id = c.challenge_id "
                         " AND cc.user_id = %s AND cc.completed_on = CURDATE()) AS done_today, "
                         "(SELECT COUNT(*) FROM challenge_completions cc WHERE cc.challenge_id = c.challenge_id "
                         " AND cc.user_id = %s) AS times_done "
                         "FROM challenges c JOIN topics t ON c.topic_id = t.topic_id "
                         "WHERE c.is_active = 1 ORDER BY c.challenge_id", (uid, uid))
    return render_template("student/challenges.html", challenges=rows)


@challenge_bp.route("/<int:challenge_id>/complete", methods=["POST"])
@login_required("student")
def complete(challenge_id):
    db, uid = get_db(), session["user_id"]
    try:
        result = complete_challenge(db, uid, challenge_id)
    except LookupError:
        abort(404)
    if result is None:
        flash("You already completed this challenge today. Come back tomorrow!", "info")
    else:
        db.commit()
        flash_rewards(result, "Challenge complete!")
    return redirect(url_for("challenge.challenge_list"))
