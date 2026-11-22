# EcoQuest — Gamified Environmental Education Platform for Schools and Colleges
### B.Tech Final Year Project Report

> **Honesty note.** This report describes what was actually built and run. Items not performed (user surveys, cloud
> deployment, performance testing, security audit) are explicitly marked *not performed / not evaluated / future work*.

## Abstract
EcoQuest is a web application that makes environmental education interactive. Students read lessons, take quizzes and
complete real-life eco challenges to earn XP, levels, badges and streaks, and compare progress on a leaderboard. Teachers
create quizzes and challenges and view class analytics; administrators manage users and content. The system uses a simple
three-tier architecture (HTML/CSS/JavaScript, Flask, MySQL). It was tested with 58 automated tests and manual browser checks.
Its educational effectiveness with real students has **not been evaluated**.

## Chapter 1 — Introduction
Environmental awareness is important for schools and colleges, but classroom delivery is often theoretical. Game elements
such as points, levels and badges are commonly used to motivate learners. EcoQuest applies these ideas to environmental topics.

## Chapter 2 — Problem Definition
Environmental education is often taught in a traditional, theoretical manner that fails to engage students, so awareness of
sustainable practices remains limited. A platform is needed that makes learning interactive, encourages action, and gives
teachers visibility of participation.

## Chapter 3 — Existing System
Typical approaches are textbooks, lectures, static websites and general-purpose quiz platforms. These generally lack a
combined learning–quiz–action–reward cycle focused on environmental topics and offer limited class-level analytics. (General
characterisation; no formal market survey was performed.)

## Chapter 4 — Proposed System
EcoQuest provides: six environmental topics with lessons; multiple-choice quizzes with answer review; eco challenges;
gamification (XP, level = floor(XP/100)+1, badges, streaks); leaderboard filterable by institution/class; topic-wise
progress charts; teacher and admin dashboards.

## Chapter 5 — Requirement Analysis
Functional and non-functional requirements, user classes and use cases are in [srs.md](srs.md). Summary: three roles with
role-based access; secure authentication; relational data storage; responsive UI.

## Chapter 6 — Feasibility Study
Technical, economic, operational, schedule and legal aspects are assessed in [project_proposal.md](project_proposal.md).
The project was found feasible using free, standard technologies.

## Chapter 7 — System Design
Three-tier architecture, component and deployment diagrams: [architecture.md](architecture.md). DFD Level 0/1, use case,
class, sequence and activity diagrams: [diagrams.md](diagrams.md). Flask blueprints separate student, quiz, challenge,
teacher and admin functionality; `utils/gamification.py` holds the business rules.

## Chapter 8 — Database Design
15 InnoDB tables with primary/foreign keys and unique constraints; ER diagram, relationships and normalisation notes are in
[database.md](database.md). Quiz data is modelled as quiz → question → option; attempts are stored in `quiz_attempts` and
`quiz_answers`; badges are N:M through `user_badges`.

## Chapter 9 — Implementation
* **Authentication:** Werkzeug password hashing, Flask sessions, `@login_required(role)` decorator, CSRF token on forms.
* **Learning:** topics → lessons → completion stored in `user_progress` → XP and badge check.
* **Quiz:** server-side grading (`grade()`), XP formula `10 × correct (+50 if perfect)`, attempt/answer persistence, result review.
* **Gamification:** `calculate_level`, `next_streak`/`update_streak` (+100 XP every 7th streak day), rule-based `check_badges`.
* **Challenges:** once-per-day completion enforced by a UNIQUE key and a code check.
* **Analytics:** SQL aggregate queries feeding Chart.js (topic progress, quiz scores, participation, challenge counts).
* **Teacher/Admin:** CRUD for quizzes, questions, challenges, users, topics, lessons and badges.
* **Game layer:** Eco City (pollution level falls as the level rises), daily quests with a bonus, level-up messages, two sorting mini-games graded on the server, and quiz instant feedback with server-side answer locking.
* **UI:** custom CSS (green palette, cards, progress bars), responsive via media queries, basic accessibility features.

## Chapter 10 — Testing
68 pytest tests (60 documented test cases) executed against a separate MySQL database; all passed in the last run
(details: [testing.md](testing.md), [../TEST_RESULTS.md](../TEST_RESULTS.md)). Manual browser checks: student dashboard,
quiz navigation, teacher dashboard charts (no console errors), landing page at 375 px width without horizontal scroll.
Not performed: load testing, formal accessibility audit, cross-browser testing, penetration testing.

## Chapter 11 — Results
The application starts, connects to MySQL, and supports the complete demonstration flow (student → lesson → quiz →
challenge → leaderboard; teacher dashboard and quiz creation; admin management). No user study was conducted, so no
claims are made about learning outcomes or engagement improvements.

## Chapter 12 — Deployment
Local deployment verified. Railway deployment prepared (`Procfile`, environment-based configuration) but **not performed**;
see [deployment.md](deployment.md).

## Chapter 13 — Limitations
No password reset or email verification; challenges are self-reported; teachers see all students (no class assignment);
Chart.js needs internet access; not load-tested or independently security-audited; cloud deployment not done;
content volume is limited to the demo data.

## Chapter 14 — Future Scope
Certificate generation, CSV/PDF reports, dark mode, institution-level competitions, class-based teacher assignment, PWA,
email-based password reset, a pilot study with real students to evaluate engagement.

## Chapter 15 — Conclusion
EcoQuest demonstrates a complete, working gamified learning platform built with simple technologies that can be explained
and defended in a viva. The project meets its functional goals as verified by automated and manual testing; evaluation with
real users remains future work.

## References
1. Flask documentation — https://flask.palletsprojects.com
2. MySQL 8.4 Reference Manual — https://dev.mysql.com/doc/
3. PyMySQL documentation — https://pymysql.readthedocs.io
4. Chart.js documentation — https://www.chartjs.org/docs/
5. IEEE Std 830-1998, Recommended Practice for Software Requirements Specifications.
6. Pressman, R. S., *Software Engineering: A Practitioner's Approach* (SDLC, Agile, testing concepts).

## Appendix
A. Demo accounts — [user_manual.md](user_manual.md) · B. Database schema — `database/schema.sql` ·
C. Test cases — [testing.md](testing.md) · D. Viva material — `VIVA_QUESTIONS.md`, `VIVA_CODING.md`
