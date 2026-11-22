# TEST RESULTS

Environment: Windows 11, Python 3.11.9, MySQL 8.4.9 (local), Flask test client, database `ecoquest_test`.

## Automated tests
Command: `python -m pytest -q` → **58 passed** (last run; ~16 s). Full per-case table: [docs/testing.md](docs/testing.md).

| File | Tests (pytest items) |
|---|---|
| tests/test_auth.py | registration, login, logout, authorization, CSRF |
| tests/test_quiz.py | grading, XP, attempt storage, result privacy |
| tests/test_gamification.py | level, XP, streak, badges, leaderboard, progress (parameterised cases included) |
| tests/test_challenges_and_admin.py | challenges, teacher and admin actions, seed integrity, FK/UNIQUE constraints |
| tests/test_smoke.py | all main pages render per role; 404 page |

A defect found by the smoke test during development (Progress page crashed for a student with no activity because PyMySQL
returns an empty tuple) was fixed in `utils/database.py` and the suite re-run.

## Manual checks (Browser pane, local server)
| Check | Result |
|---|---|
| Student login and dashboard from DB data | Rendered correctly |
| Quiz question navigation (JS) | Next button, counter and answered-state worked |
| Teacher dashboard charts (Chart.js) | Rendered; no console errors |
| Landing page at 375 px width | No horizontal scroll |

## Not tested
Cross-browser, load/performance, formal accessibility audit, penetration testing, cloud deployment.
