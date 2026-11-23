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
| Student | Register/login, dashboard with **Eco City** and **daily quests**, topics & lessons, quizzes with instant feedback and combos, challenges, **mini-games** (Waste Sorting Rush, Pollution Detective), XP & levels with level-up celebrations, badges, daily streak, leaderboard (class/institution filter), progress charts, profile |
| Teacher | Dashboard with 4 charts, student list & detail, create quizzes/questions, create challenges |
| Admin | Statistics, manage users, topics, lessons, badges (+ all teacher pages) |

Built-in content: 6 environmental topics (Climate Change, Pollution, Waste Management, Water Conservation, Renewable Energy, Biodiversity), 12 lessons, 6 quizzes (32 questions), 12 challenges, 2 mini-games and 9 badges. Admins and teachers can add more topics, lessons, quizzes and challenges from their pages.

## How it is gamified
* **XP and levels** (level = floor(XP/100)+1) with a level-up celebration.
* **Eco City:** your city starts smoggy (95% pollution) and gets cleaner as you level up.
* **Daily quests:** lesson, quiz, challenge and mini-game; finish all four for +25 XP.
* **Mini-games:** timed sorting rounds with combos and instant feedback (XP once per game per day).
* **Quizzes:** instant right/wrong feedback, explanations and combo counter (answers are locked on the server).
* **Badges, streaks (+100 XP every 7 days) and a leaderboard.**

## Technology stack
HTML5 · CSS3 · vanilla JavaScript · Chart.js (CDN) · Python 3.11 · Flask · PyMySQL · MySQL 8 · pytest · Git

## Architecture
Three tiers: Browser (HTML/CSS/JS) → Flask (routes + business logic) → MySQL. See [docs/architecture.md](docs/architecture.md).

## New in v3
* **Eco Pulse — Kolkata:** live Air Quality Index (Open-Meteo, US AQI, modelled data) as a daily prediction game (+15 XP correct, +5 for checking in), 7-day AQI chart, health tips and an eco fact of the day. Works offline with the last saved reading.
* **Quest Map:** every topic is a world from Beginner to Advanced; quizzes are boss levels with 1–3 stars.
* **More content:** 21 lessons (incl. AQI, PM2.5, Kolkata's mangroves and wetlands), 13 quizzes at three difficulty levels, 18 challenges, 19 badges.
* **5 mini-games:** Waste Sorting Rush, Pollution Detective, Eco Myth Buster, Renewable or Not?, Water Wise.
* **Weekly XP goal (+50 bonus), 4-week activity calendar, printable certificates (Eco Learner / Guardian / Champion).**
* **Accounts:** change password; admin password reset. **Teachers:** announcements, CSV export of class results. **Students:** CSV export of their progress.
* **Dark mode, sound effects (mute button), automatic database backup when the desktop app closes.**

## EcoQuest as a Windows application
EcoQuest can run as a normal Windows program (own window, no browser, no address bar):

```powershell
powershell -ExecutionPolicy Bypass -File build_exe.ps1     # builds dist\EcoQuest\EcoQuest.exe (PyInstaller + WebView2)
powershell -ExecutionPolicy Bypass -File install_app.ps1   # installs to %LOCALAPPDATA%\Programs\EcoQuest + Desktop/Start Menu shortcuts
```
Open **EcoQuest** from the desktop or Start Menu. It starts the MySQL database and the app by itself, and stops them when you close the window.
Remove it with `uninstall_app.ps1` (your data is kept). Charts work offline (Chart.js is bundled). It still needs MySQL 8.4 installed on the PC.

## Using EcoQuest on your PC (no terminal, no Claude Code needed)
After the one-time setup below, everything works from the desktop:

| Shortcut / file | What it does |
|---|---|
| **EcoQuest** (desktop, `EcoQuest.vbs`) | Starts MySQL and the app if they are not running, then opens http://127.0.0.1:5000 |
| **EcoQuest - Stop** (desktop, `EcoQuest_Stop.vbs`) | Stops the app and the database cleanly |
| `EcoQuest_Backup.vbs` | Saves a full database backup to the `backups` folder |
| `EcoQuest_Create_Admin.bat` | Creates your own admin / teacher account |

Needs Python 3.11, MySQL 8.4 (data folder `%USERPROFILE%\ecoquest-mysql-data`) and this project folder where it is now. The app runs on the Waitress server (`run_server.py`); logs are in `logs/server.log`.

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
Uses a separate `ecoquest_test` database. 68 automated tests (60 documented test cases) — see [docs/testing.md](docs/testing.md) and [TEST_RESULTS.md](TEST_RESULTS.md).

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
