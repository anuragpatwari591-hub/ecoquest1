"""Eco mini-games: list, play and finish."""
from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   session, url_for)

from utils.auth import login_required
from utils.database import fetch_one, get_db
from utils.gamification import record_activity
from utils.games import (GAMES, game_xp, grade_game, items_for_client,
                         pick_items)
from utils.ui import flash_rewards

games_bp = Blueprint("games", __name__, url_prefix="/games")


def _game_or_404(key):
    if key not in GAMES:
        abort(404)
    return GAMES[key]


def played_today(db, user_id, title):
    """XP from a given game can be earned once per day (replays are still allowed for fun)."""
    return fetch_one(db, "SELECT 1 AS x FROM activity_log WHERE user_id = %s AND activity = 'game' "
                         "AND description LIKE %s AND DATE(created_at) = CURDATE()",
                     (user_id, f"Game: {title}%")) is not None


@games_bp.route("/")
@login_required("student")
def game_list():
    db, uid = get_db(), session["user_id"]
    games = [dict(key=k, done_today=played_today(db, uid, g["title"]), **g) for k, g in GAMES.items()]
    return render_template("student/games.html", games=games)


@games_bp.route("/<key>")
@login_required("student")
def play(key):
    game = _game_or_404(key)
    item_ids = pick_items(key)
    session[f"game_{key}"] = item_ids               # the server remembers which items were dealt
    return render_template("student/game_play.html", key=key, game=game,
                           items=items_for_client(key, item_ids))


@games_bp.route("/<key>/finish", methods=["POST"])
@login_required("student")
def finish(key):
    game = _game_or_404(key)
    db, uid = get_db(), session["user_id"]
    item_ids = session.pop(f"game_{key}", None)
    if not item_ids:                                # refresh / double submit: nothing to grade
        flash("That round has already been scored. Start a new round!", "info")
        return redirect(url_for("games.game_list"))
    answers = {i: request.form.get(f"ans_{i}") for i in item_ids}
    score, total, review = grade_game(key, item_ids, answers)
    xp, result = 0, None
    if not played_today(db, uid, game["title"]):
        xp = game_xp(score, total)
        result = record_activity(db, uid, xp, "game", f"Game: {game['title']} {score}/{total}")
        db.commit()
        flash_rewards(result, f"Round complete!")
    bin_names = {b[0]: b[1] for b in game["bins"]}
    return render_template("student/game_result.html", key=key, game=game, score=score, total=total,
                           review=review, xp=xp, xp_locked=result is None, bin_names=bin_names)
