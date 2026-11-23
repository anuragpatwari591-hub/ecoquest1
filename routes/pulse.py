"""Eco Pulse: Kolkata's live air quality as a daily prediction game + eco brief."""
from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

import config
from utils import pulse
from utils.auth import login_required
from utils.database import execute, fetch_all, fetch_one, get_db
from utils.gamification import record_activity
from utils.ui import flash_rewards

pulse_bp = Blueprint("pulse", __name__, url_prefix="/pulse")


def todays_checkin(db, user_id):
    return fetch_one(db, "SELECT description, xp_change FROM activity_log WHERE user_id = %s AND activity = 'pulse' "
                         "AND DATE(created_at) = CURDATE() ORDER BY log_id DESC LIMIT 1", (user_id,))


def store_reading(db, data):
    execute(db, "INSERT IGNORE INTO air_readings (city, observed_at, us_aqi, pm2_5, pm10) VALUES (%s,%s,%s,%s,%s)",
            (pulse.CITY["name"], data["time"], data["aqi"], data["pm25"], data["pm10"]))
    db.commit()


def last_stored(db):
    return fetch_one(db, "SELECT * FROM air_readings WHERE city = %s ORDER BY observed_at DESC LIMIT 1", (pulse.CITY["name"],))


@pulse_bp.route("/")
@login_required("student", "teacher")
def index():
    db = get_db()
    data = pulse.get_air()
    if data:
        store_reading(db, data)
    stored = None if data else last_stored(db)
    is_student = session.get("role") == "student"
    checkin = todays_checkin(db, session["user_id"]) if is_student else None
    reveal = (not is_student) or checkin is not None
    aqi = data["aqi"] if data else (stored["us_aqi"] if stored else None)
    cat = pulse.category(aqi) if aqi is not None else None
    recent = fetch_all(db, "SELECT description, xp_change, created_at FROM activity_log WHERE user_id = %s AND activity = 'pulse' "
                           "ORDER BY log_id DESC LIMIT 7", (session["user_id"],))
    return render_template("pulse.html", data=data, stored=stored, aqi=aqi, cat=cat, reveal=reveal, checkin=checkin,
                           is_student=is_student, fact=pulse.daily_fact(), tips=pulse.TIPS.get(cat["name"], []) if cat else [],
                           guesses=pulse.GUESSES, city=pulse.CITY["name"], source=pulse.SOURCE, recent=recent,
                           categories=pulse.CATEGORIES, xp_ok=config.XP_PULSE_CORRECT, xp_try=config.XP_PULSE_TRY,
                           today=date.today())


@pulse_bp.route("/guess", methods=["POST"])
@login_required("student")
def guess():
    db, uid = get_db(), session["user_id"]
    choice = request.form.get("guess")
    if choice not in pulse.GUESSES:
        flash("Choose one of the options.", "danger")
        return redirect(url_for("pulse.index"))
    if todays_checkin(db, uid):
        flash("You already made today's prediction. Come back tomorrow!", "info")
        return redirect(url_for("pulse.index"))
    data = pulse.get_air()
    if not data:
        flash("Live air-quality data is unavailable right now (internet needed), so no XP can be awarded. Try again later.", "warning")
        return redirect(url_for("pulse.index"))
    actual = pulse.guess_group(data["aqi"])
    correct = choice == actual
    xp = config.XP_PULSE_CORRECT if correct else config.XP_PULSE_TRY
    cat = pulse.category(data["aqi"])["name"]
    result = record_activity(db, uid, xp, "pulse",
                             f"Eco Pulse: predicted {pulse.GUESSES[choice]}; actual AQI {data['aqi']} ({cat})")
    db.commit()
    flash_rewards(result, "🎯 Spot on!" if correct else "Checked in! Not quite this time.")
    return redirect(url_for("pulse.index"))
