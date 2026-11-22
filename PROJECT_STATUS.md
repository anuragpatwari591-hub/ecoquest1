# PROJECT STATUS

**Current phase:** Core build, testing and documentation complete. Remaining: GitHub push and cloud deployment (need the owner's accounts).

## Actually implemented
Authentication (register/login/logout, hashing, sessions, roles, CSRF) · student dashboard · topics/lessons/completion · quizzes (listing,
instructions, one-question navigation, server grading, result review, history) · XP/levels/streak/badges · challenges (once per day) ·
leaderboard (institution/class filter) · progress charts · teacher dashboard (4 charts), students, quiz/question/challenge management ·
admin dashboard, users, topics, lessons, badges · responsive UI · environmental content (6 topics, 12 lessons, 6 quizzes/32 questions, 12 challenges, 9 badges); game layer: Eco City, daily quests, level-up messages, two mini-games, quiz instant feedback with server-side answer locking; `create_admin.py` for real admin accounts; demo accounts only with `init_db.py --demo`.

## Actually tested
* `python -m pytest` → **68 passed** (last run, local MySQL 8.4.9, Windows 11, Python 3.11.9).
* Manual (Browser pane): student login → dashboard renders from DB; quiz navigation JS works; teacher dashboard charts render, no console errors;
  landing page has no horizontal overflow at 375 px.

## Statically verified / written but not run
* `Procfile` and Railway variable fallbacks in `config.py` (not run on Railway).

## Not tested
Cross-browser; load/performance; accessibility audit; admin forms in a real browser (admin pages are covered by automated render tests; create/delete actions for users, topics and lessons by automated tests; badge and quiz/challenge-edit forms only partly).
Full manual walk-through of every page at tablet/mobile widths (only the landing page was checked on mobile).

## Not implemented / future work
Password reset/email verification; certificates; CSV/PDF export; dark mode; PWA; class-based teacher assignment; admin editing of quiz metadata
(quizzes can be created, questions added/deleted, quizzes deleted).

## Known issues / limitations
* Landing-page hero card shows illustrative example values (static, labelled as preview in design; not database data).
* Charts need internet access (Chart.js CDN).
* Flask development server used locally; gunicorn configured for deployment but untested on Windows (Linux-only server).

## Deployment status
Local only. GitHub: local git repository with commits; pushed to https://github.com/anuragpatwari591-hub/ecoquest1 (branch master). Railway: **not deployed**.

## Documentation status
README, SRS + use cases, proposal/feasibility, architecture (component/deployment), DFD 0/1, ER, UML (class/sequence/activity), database,
testing (60 test cases with real results), deployment, user manual, developer guide, final report, presentation outline/deck,
VIVA_QUESTIONS (118 Q&A), VIVA_CODING (18 coding tasks).

## Next logical actions
1. Owner creates a GitHub repository and authenticates → push.
2. Owner creates a Railway project → deploy, then verify and record the URL.
3. Take screenshots for the report/presentation.
4. Rehearse viva using the viva files.
