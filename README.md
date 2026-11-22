# 🌱 EcoQuest — Gamified Environmental Education Platform

**Learn. Play. Act. Make an Impact.**
B.Tech Final Year Project · Flask + MySQL + HTML/CSS/JavaScript

## Problem statement
Environmental education is often taught in a traditional, theoretical way that fails to engage students, so awareness about
sustainability remains limited. EcoQuest is an interactive platform designed to improve engagement, awareness and
participation by combining lessons, quizzes, real-life challenges and gamification.

## Objectives
* Make environmental learning interactive and rewarding (XP, levels, badges, streaks, leaderboard).
* Provide structured lessons and quizzes on six environmental topics.
* Give students measurable progress; give teachers class-level visibility; give admins content/user management.
* Use simple, defendable technologies appropriate for a B.Tech project.

## Features
| Role | Features |
|---|---|
| Student | Register/login, dashboard, topics & lessons, quizzes with review, challenges, XP & levels, badges, daily streak, leaderboard (class/institution filter), progress charts, profile |
| Teacher | Dashboard with 4 charts, student list & detail, create quizzes/questions, create challenges |
| Admin | Statistics, manage users, topics, lessons, badges (+ all teacher pages) |

Built-in content: 6 environmental topics + 13 B.Tech study subjects (CSE/IT core and first-year common) = 51 lessons, 19 quizzes (110 questions), 20 challenges, 11 badges. The B.Tech lessons are original concise revision notes; admins can add more subjects, lessons and quizzes from the Admin pages.

## Technology stack
HTML5 · CSS3 · vanilla JavaScript · Chart.js (CDN) · Python 3.11 · Flask · PyMySQL · MySQL 8 · pytest · Git

## Architecture
Three tiers: Browser (HTML/CSS/JS) → Flask (routes + business logic) → MySQL. See [docs/architecture.md](docs/architecture.md).

## Installation & local run
```powershell
pip install -r requirements.txt
copy .env.example .env        # edit DB_* values and SECRET_KEY
python init_db.py             # creates/upgrades tables and loads study content (no fake users)
python create_admin.py        # create YOUR admin account (asks for name, email, password)
python app.py                 # open http://127.0.0.1:5000
# optional, for demonstrations only: python init_db.py --demo  (adds fictional demo accounts + sample classmates)
```
Database setup details: [docs/deployment.md](docs/deployment.md) · schema: [database/schema.sql](database/schema.sql).

## Environment variables
`DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, SECRET_KEY, FLASK_DEBUG, SESSION_COOKIE_SECURE` — see `.env.example`. Never commit `.env`.

## Demo accounts (only if you ran `python init_db.py --demo`)
| Role | Email | Password |
|---|---|---|
| Admin | admin@ecoquest.test | Admin@123 |
| Teacher | teacher@ecoquest.test | Teacher@123 |
| Student | student@ecoquest.test | Student@123 |

## Testing
```powershell
python -m pytest -v
```
Uses a separate `ecoquest_test` database. 62 automated tests (54 documented test cases) — see [docs/testing.md](docs/testing.md) and [TEST_RESULTS.md](TEST_RESULTS.md).

## Deployment
Prepared for Railway (`Procfile`, environment-based config) but **not deployed**. See [docs/deployment.md](docs/deployment.md).

## Project structure
See [docs/developer_guide.md](docs/developer_guide.md).

## Documentation
[SRS & use cases](docs/srs.md) · [Proposal & feasibility](docs/project_proposal.md) · [Diagrams (DFD, UML)](docs/diagrams.md) ·
[Database & ER](docs/database.md) · [Architecture](docs/architecture.md) · [Testing](docs/testing.md) ·
[Deployment](docs/deployment.md) · [User manual](docs/user_manual.md) · [Developer guide](docs/developer_guide.md) ·
[Final report](docs/final_report.md) · [Presentation outline](docs/presentation_outline.md) ·
[Viva questions](VIVA_QUESTIONS.md) · [Coding viva](VIVA_CODING.md)

## Limitations
* No email verification or password reset; teachers are not linked to specific classes (they see all students).
* Streak/XP are computed per activity; no anti-cheating beyond one challenge completion per day (challenges are self-reported).
* Charts need internet access (Chart.js CDN). Not load-tested. Not independently security-audited.
* Cloud deployment not performed.

## Future scope
Certificates, CSV/PDF export, dark mode, institution-level competitions, class-based teacher assignment, PWA, password reset.

## Contributors
Anurag Patwari — B.Tech Final Year Project.
