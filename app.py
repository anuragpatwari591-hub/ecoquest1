"""EcoQuest - Flask application entry point."""
import os
import secrets

from flask import Flask, abort, render_template, request, session

import config
from utils.database import close_db, fetch_all, fetch_one, get_db


def create_app(testing=False):
    app = Flask(__name__)
    app.config.from_object(config)
    app.config["TESTING"] = testing
    app.config["CSRF_ENABLED"] = not testing

    app.teardown_appcontext(close_db)

    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.quiz import quiz_bp
    from routes.challenge import challenge_bp
    from routes.games import games_bp
    from routes.pulse import pulse_bp
    from routes.extras import extras_bp
    from routes.teacher import teacher_bp
    from routes.admin import admin_bp
    for bp in (auth_bp, student_bp, quiz_bp, challenge_bp, games_bp, pulse_bp, extras_bp, teacher_bp, admin_bp):
        app.register_blueprint(bp)

    # ---- CSRF protection: every POST must carry the token stored in the session
    @app.before_request
    def check_csrf():
        if request.method == "POST" and app.config["CSRF_ENABLED"]:
            token = session.get("csrf_token")
            if not token or token != request.form.get("csrf_token"):
                abort(400, "Invalid or missing form token. Please go back and try again.")

    @app.context_processor
    def inject_globals():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(16)
        return {"csrf_token": session["csrf_token"]}

    @app.route("/")
    def index():
        db = get_db()
        topics = fetch_all(db, "SELECT * FROM topics ORDER BY topic_id")
        stats = fetch_one(db, "SELECT (SELECT COUNT(*) FROM lessons) AS lessons, "
                              "(SELECT COUNT(*) FROM quizzes) AS quizzes, "
                              "(SELECT COUNT(*) FROM challenges WHERE is_active = 1) AS challenges, "
                              "(SELECT COUNT(*) FROM badges) AS badges")
        return render_template("index.html", topics=topics, stats=stats)

    @app.errorhandler(400)
    def bad_request(e):
        return render_template("error.html", code=400, message=getattr(e, "description", "Bad request")), 400

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, message="The page you are looking for does not exist."), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", code=500, message="Something went wrong on our side. Please try again."), 500

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0" if not config.DEBUG else "127.0.0.1", port=port, debug=config.DEBUG)
