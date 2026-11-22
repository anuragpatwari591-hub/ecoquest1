"""Game mechanics tests: mini-games, quiz feedback lock, Eco City, daily quests, level-up (TC-51 .. TC-60)."""
from conftest import one, user_id
from utils import gamification as g
from utils.games import GAMES, grade_game, game_xp


def _play(client, key, correct=True):
    """Start a round, then submit all answers right (or all wrong)."""
    assert client.get(f"/games/{key}").status_code == 200
    with client.session_transaction() as s:
        ids = s[f"game_{key}"]
    lookup = {i[0]: i[3] for i in GAMES[key]["items"]}
    bins = [b[0] for b in GAMES[key]["bins"]]
    data = {f"ans_{i}": (lookup[i] if correct else next(b for b in bins if b != lookup[i])) for i in ids}
    return client.post(f"/games/{key}/finish", data=data), len(ids)


def test_game_pages_render(student):                                      # TC-51
    assert student.get("/games/").status_code == 200
    assert student.get("/games/waste-sort").status_code == 200
    assert student.get("/games/unknown").status_code == 404


def test_perfect_game_round_awards_xp_and_badge(student, db):             # TC-52
    r, n = _play(student, "waste-sort")
    assert r.status_code == 200 and b"Round complete" in r.data
    uid = user_id(db)
    assert one(db, "SELECT total_xp FROM users WHERE user_id=%s", (uid,))["total_xp"] == n * 5 + 10
    badge = one(db, "SELECT COUNT(*) AS n FROM user_badges ub JOIN badges b ON ub.badge_id=b.badge_id "
                    "WHERE ub.user_id=%s AND b.name='Game On'", (uid,))
    assert badge["n"] == 1


def test_game_xp_only_once_per_day_per_game(student, db):                 # TC-53
    _play(student, "waste-sort")
    r, _ = _play(student, "waste-sort")                                   # second round: practice only
    assert b"practice" in r.data
    assert one(db, "SELECT total_xp FROM users WHERE user_id=%s", (user_id(db),))["total_xp"] == 8 * 5 + 10


def test_wrong_answers_score_zero(student, db):                           # TC-54
    r, n = _play(student, "pollution-detective", correct=False)
    assert b"0/8" in r.data
    assert one(db, "SELECT total_xp FROM users WHERE user_id=%s", (user_id(db),))["total_xp"] == 0


def test_finish_without_round_is_ignored(student, db):                    # TC-55
    r = student.post("/games/waste-sort/finish", data={"ans_bottle": "recycle"})
    assert r.status_code == 302
    assert one(db, "SELECT total_xp FROM users WHERE user_id=%s", (user_id(db),))["total_xp"] == 0


def test_grade_game_unit():                                               # TC-56
    ids = ["bottle", "peel"]
    score, total, review = grade_game("waste-sort", ids, {"bottle": "recycle", "peel": "ewaste"})
    assert (score, total) == (1, 2) and review[1]["ok"] is False
    assert game_xp(8, 8) == 50 and game_xp(3, 8) == 15
    # an invalid bin counts as unanswered
    assert grade_game("waste-sort", ["bottle"], {"bottle": "nonsense"})[0] == 0


def test_quiz_check_locks_first_answer(student, db):                      # TC-57
    student.get("/quiz/3/take")
    q = one(db, "SELECT question_id FROM questions WHERE quiz_id=3 ORDER BY question_id LIMIT 1")["question_id"]
    opts = {o["is_correct"]: o["option_id"] for o in _opts(db, q)}
    wrong, right = opts[0], opts[1]
    r1 = student.post("/quiz/3/check", data={"question_id": q, "option_id": wrong}).get_json()
    assert r1["is_correct"] is False and r1["correct_id"] == right
    r2 = student.post("/quiz/3/check", data={"question_id": q, "option_id": right}).get_json()
    assert r2["chosen"] == wrong and r2["is_correct"] is False            # cannot switch after seeing the answer
    student.post("/quiz/3/submit", data={f"q_{q}": right})                # submit tries the right option anyway
    attempt = one(db, "SELECT score FROM quiz_attempts ORDER BY attempt_id DESC LIMIT 1")
    assert attempt["score"] == 0                                          # the locked (wrong) choice is graded


def _opts(db, qid):
    db.commit()
    with db.cursor() as cur:
        cur.execute("SELECT option_id, is_correct FROM options WHERE question_id=%s", (qid,))
        return cur.fetchall()


def test_quiz_check_rejects_foreign_option(student, db):                  # TC-58
    q1 = one(db, "SELECT question_id FROM questions WHERE quiz_id=3 ORDER BY question_id LIMIT 1")["question_id"]
    foreign = one(db, "SELECT option_id FROM options WHERE question_id<>%s LIMIT 1", (q1,))["option_id"]
    assert student.post("/quiz/3/check", data={"question_id": q1, "option_id": foreign}).status_code == 400


def test_city_stage_gets_cleaner_with_level():                            # TC-59
    assert g.city_stage(1)["pollution"] == 95 and g.city_stage(1)["name"] == "Smoggy Town"
    assert g.city_stage(5)["pollution"] == 55
    assert g.city_stage(10)["pollution"] == 5 and g.city_stage(10)["name"] == "Eco City"
    assert g.city_stage(1)["air"] == "Poor" and g.city_stage(10)["air"] == "Excellent"


def test_daily_quests_bonus_and_level_up(student, db):                    # TC-60
    uid = user_id(db)
    with db.cursor() as cur:
        cur.execute("UPDATE users SET total_xp = 85 WHERE user_id = %s", (uid,))
    db.commit()
    student.post("/student/lessons/1/complete")                           # +10 -> 95 (quest 1)
    student.post("/challenges/1/complete")                                # +20 -> level 2 (quest 2)
    student.post("/quiz/3/submit", data={})                               # 0 XP but counts as a quiz (quest 3)
    quests = g.daily_quests(db, uid)
    assert quests["done"] == 3 and not quests["all_done"]
    r, n = _play(student, "waste-sort")                                   # quest 4 -> bonus
    assert one(db, "SELECT COUNT(*) AS n FROM activity_log WHERE user_id=%s AND activity='quest'", (uid,))["n"] == 1
    xp = one(db, "SELECT total_xp FROM users WHERE user_id=%s", (uid,))["total_xp"]
    assert xp == 85 + 10 + 20 + 0 + (n * 5 + 10) + 25
