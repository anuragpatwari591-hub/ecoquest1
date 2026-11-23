# Software Requirements Specification (IEEE 830 style)
**Project:** EcoQuest — Gamified Environmental Education Platform for Schools and Colleges

## 1. Introduction
### 1.1 Purpose
This SRS describes the requirements of EcoQuest, a web application that makes environmental education interactive through
lessons, quizzes, challenges and gamification (XP, levels, badges, streaks, leaderboards).
### 1.2 Scope
EcoQuest lets students learn and practise environmental topics, lets teachers create quizzes/challenges and monitor
participation, and lets administrators manage users and content. It is designed to improve engagement, awareness and
participation in environmental education. It does not claim to solve environmental problems.
### 1.3 Definitions
| Term | Meaning |
|---|---|
| XP | Experience points awarded for activities |
| Level | `floor(XP / 100) + 1` |
| Streak | Number of consecutive days with at least one eligible activity |
| Badge | Achievement unlocked automatically when a rule is satisfied |
| Challenge | A real-life eco action the student marks as completed |
### 1.4 References
IEEE 830-1998 SRS recommended practice; Flask, MySQL and Chart.js documentation.

## 2. Overall Description
### 2.1 Product perspective
Stand-alone, three-tier web application: browser → Flask → MySQL (see `architecture.md`).
### 2.2 Product functions
Authentication; learning module; quiz module; challenges; gamification; progress analytics; leaderboard; teacher tools; admin tools.
### 2.3 User classes
| Class | Description |
|---|---|
| Student | Learns, plays quizzes, completes challenges |
| Teacher | Creates quizzes/challenges, views student performance |
| Admin | Manages users, topics, lessons, badges and all content |
### 2.4 Operating environment
Server: Python 3.11+, Flask, MySQL 8. Client: any modern browser (desktop, tablet, mobile). Charts need internet access to load Chart.js from a CDN.
### 2.5 Design constraints
Simple, curriculum-level technologies only: HTML/CSS/JavaScript, Python/Flask, MySQL. No JavaScript framework, no ORM, no external APIs.
### 2.6 Assumptions and dependencies
Users have a browser and internet access; MySQL is available; environment variables supply credentials. Dependencies: Flask, PyMySQL, python-dotenv, gunicorn (deployment), Chart.js (CDN).

## 3. Functional Requirements
| ID | Requirement | Status |
|---|---|---|
| FR-1 | Students can register with name, email, password (min 6 chars), optional institution/class | Implemented, tested |
| FR-2 | Users can log in/out; passwords are hashed; sessions identify users | Implemented, tested |
| FR-3 | Role-based authorisation for student/teacher/admin pages | Implemented, tested |
| FR-4 | Students can browse topics, read lessons (intro, explanation, key points, eco-tip) | Implemented, manually verified |
| FR-5 | Completing a lesson stores completion, awards 10 XP, updates progress, checks badges | Implemented, tested |
| FR-6 | Students can attempt quizzes of 4-option MCQs with question navigation | Implemented, navigation manually verified |
| FR-7 | Server calculates score, accuracy, XP (10/correct + 50 perfect bonus), stores attempt and answers | Implemented, tested |
| FR-8 | Result page shows score, accuracy, XP and answer review; history of attempts | Implemented, tested |
| FR-9 | Level = floor(XP/100)+1 with progress bar to next level | Implemented, tested |
| FR-10 | Daily streak; +100 XP when streak reaches a multiple of 7 | Implemented, tested |
| FR-11 | Badges unlock automatically (6+ rule-based badges) | Implemented, tested |
| FR-12 | Challenges can be completed once per day, awarding the challenge XP | Implemented, tested |
| FR-13 | Leaderboard by XP (SQL sorting) with institution/class filters | Implemented, tested |
| FR-14 | Topic-level progress % and charts (topic progress, quiz scores, XP/day) | Implemented, manually verified |
| FR-15 | Teacher dashboard (students, active, avg score, attempts, challenges) with 4 charts | Implemented, manually verified |
| FR-16 | Teacher can view students, create quizzes, add/delete questions, create challenges | Implemented, tested |
| FR-17 | Admin dashboard with platform statistics and charts | Implemented, manually verified |
| FR-19 | Eco City visualisation that reflects the level; daily quests with a bonus; level-up notification | Implemented, tested |
| FR-20 | Two mini-games graded on the server with a once-per-day XP cap | Implemented, tested |
| FR-21 | Quiz instant feedback with server-side answer locking | Implemented, tested |
| FR-18 | Admin can manage users, topics, lessons, quizzes/questions (via teacher pages), challenges, badges | Implemented, partly tested |

## 4. Non-Functional Requirements
| ID | Requirement | How addressed |
|---|---|---|
| NFR-1 Usability | Clean, responsive, accessible UI | CSS media queries, labels, skip link, keyboard-friendly controls |
| NFR-2 Security | Protect credentials and data | Hashing, sessions, role checks, parameterised SQL, CSRF tokens, env-var secrets |
| NFR-3 Performance | Pages respond quickly for class-sized use | Indexed FK/XP columns, one connection per request. **Not load-tested** |
| NFR-4 Reliability | Data integrity | Foreign keys, UNIQUE keys, transactions committed once per action |
| NFR-5 Maintainability | Understandable code | Blueprints, small helper modules, comments |
| NFR-6 Portability | Runs on Windows/Linux | Pure Python + MySQL; verified on Windows only |
| NFR-7 Accessibility | Basic WCAG-style practices | Labels, headings, aria attributes, colour contrast. **No formal audit** |

## 5. External Interface Requirements
* **User interface:** HTML pages rendered by Jinja2; Chart.js charts.
* **Database interface:** PyMySQL connection configured via environment variables.
* **Hardware interface:** none. **Communication:** HTTP(S).

## 6. Security Requirements
Passwords never stored in plain text; unauthenticated users cannot reach protected pages; students cannot access teacher/admin pages; teachers cannot access admin pages; all SQL parameterised; secrets not committed.

## 7. Database Requirements
MySQL 8 with 15 tables, primary/foreign keys, NOT NULL and UNIQUE constraints (see `database.md`).

## 8. Acceptance Criteria
The full demo flow (student → teacher → admin) works; automated tests pass; documentation matches the implementation (see `testing.md`, `PROJECT_STATUS.md`).

## 9. Future Scope
Certificate generation, CSV/PDF export, dark mode, institution-level competitions, PWA support, teacher-owned classes, password-reset by email.

---

# Use Case Specifications

| UC | Name | Actor | Main flow | Alternate flow |
|---|---|---|---|---|
| UC-1 | Register | Student | Open Register, enter details, submit → account created, redirected to login | Invalid data or duplicate email → error shown |
| UC-2 | Login | All | Enter email/password → redirected to own dashboard | Wrong credentials → error |
| UC-3 | Complete lesson | Student | Open topic → lesson → "Mark as complete" → XP added, progress updated, badge check | Already completed → informational message |
| UC-4 | Take quiz | Student | Open quiz → Start → answer with navigation → Submit → result with review | Unanswered questions → confirmation prompt |
| UC-5 | Complete challenge | Student | Open Challenges → Mark complete → XP awarded | Already done today → refused |
| UC-6 | View leaderboard | Student/Teacher | Open Leaderboard, optionally filter by institution/class | No students match → empty message |
| UC-7 | Create quiz | Teacher/Admin | Quizzes → fill title/topic/description → add questions with 4 options and correct choice | Missing fields → validation error |
| UC-8 | View student performance | Teacher/Admin | Students → View → see XP, topic progress, attempts, badges | — |
| UC-9 | Manage users | Admin | Users → add user / disable / delete | Cannot disable/delete self |
| UC-10 | Manage content | Admin | Topics, Lessons, Badges pages: create, edit, delete | Duplicate names rejected |

# Functional / Non-functional requirements
Listed in sections 3 and 4 above.

## Version 3 functional requirements
| ID | Requirement | Status |
|---|---|---|
| FR-22 | Eco Pulse: daily prediction game on Kolkata's live AQI with tips, facts and a seven-day chart | Implemented, tested |
| FR-23 | Quest Map with Beginner/Intermediate/Advanced levels and star ratings | Implemented, tested |
| FR-24 | Weekly XP goal with bonus; activity calendar; printable certificates | Implemented, tested |
| FR-25 | Password change, admin password reset, CSV exports, teacher announcements | Implemented, tested |
| FR-26 | Dark mode, sound effects and automatic backup in the desktop application | Implemented (backup and UI checked manually) |
