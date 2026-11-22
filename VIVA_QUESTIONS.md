# EcoQuest — Viva Questions and Answers

Answers are short and tied to this project's actual implementation.

## A. Project-specific (1–30)
1. **Why EcoQuest?** Environmental education is mostly theoretical and unengaging. EcoQuest makes it interactive with lessons, quizzes, challenges and rewards.
2. **Why gamification?** Points, levels, badges and streaks give immediate feedback and motivation, which encourages regular participation.
3. **Who are the users?** Students, teachers and administrators (three roles in the `roles` table).
4. **Why Flask?** It is a small, easy-to-understand Python framework; routes, templates and sessions are all we need. It is not over-engineered for the scope.
5. **Why MySQL?** The data is relational (users, quizzes, questions, attempts). MySQL gives foreign keys, constraints and SQL joins/aggregates, which are part of our syllabus.
6. **Why not React?** The UI is mostly server-rendered pages with little client logic. Plain HTML/CSS/JS meets the requirement and I can fully explain it. Our answer: the selected architecture fulfils the requirements while remaining maintainable and appropriate for our scope and expertise.
7. **Why not use AI/ML?** No requirement needs it; adding it would not solve a project problem and could not be defended.
8. **What is the architecture?** Three tiers: browser (HTML/CSS/JS) → Flask (routes + business logic) → MySQL.
9. **How does XP work?** Lesson +10, each correct quiz answer +10, perfect quiz +50 bonus, challenge XP as defined per challenge, 7-day streak +100. Values are in `config.py`.
10. **How is the level calculated?** `level = floor(xp / 100) + 1`; implemented in `calculate_level()`.
11. **How is progress to the next level shown?** `xp % 100` is the XP inside the level; percent = that value (since a level needs 100 XP).
12. **How does the leaderboard work?** SQL query on students ordered by `total_xp DESC`; rank is the position in the result; filters add `WHERE institution=%s / class_name=%s`.
13. **How are badges awarded?** After each activity `check_badges()` loops over badges the user does not own, computes the user's value for the badge rule (e.g. lesson count) and inserts into `user_badges` when it is ≥ the required value.
14. **How does authentication work?** Register stores a password hash; login verifies it with `check_password_hash` and stores `user_id`, `name`, `role` in the Flask session.
15. **How are roles enforced?** The `@login_required("role")` decorator checks the session and redirects if the role is not allowed.
16. **How does progress work?** Per topic: (completed lessons + attempted quizzes + completed challenges) ÷ (total lessons + quizzes + active challenges) × 100.
17. **How does the streak work?** Activity on consecutive dates increments the streak; missing a day resets it to 1; same-day activity changes nothing.
18. **How is duplicate challenge completion prevented?** A UNIQUE key on (user, challenge, date) plus a check in code: one completion per day.
19. **Where is quiz scoring done?** On the server in `grade()`; the browser never receives the correct answers during the quiz.
20. **What happens if someone tampers with an option id?** `grade()` only accepts an option that belongs to that question; otherwise the answer counts as unanswered.
21. **What are the limitations?** No password reset/email verification, self-reported challenges, teachers see all students, not load-tested, not deployed to cloud.
22. **Future scope?** Certificates, CSV/PDF export, dark mode, class-based teachers, institution competitions, PWA.
23. **How many tables?** 15 tables (roles, users, topics, lessons, quizzes, questions, options, quiz_attempts, quiz_answers, challenges, challenge_completions, badges, user_badges, user_progress, activity_log).
24. **Why store total_xp in users?** It is a derived value kept for fast leaderboard queries; every change is also recorded in `activity_log`.
25. **How did you test?** pytest with 58 tests against a separate MySQL test database, plus manual browser checks.
26. **How is the demo data created?** `init_db.py` runs `schema.sql` then inserts seed data from `seed_data.py`; passwords are hashed.
27. **What development model did you use?** Agile incremental: seven increments from requirements to testing.
28. **How is the app configured?** `config.py` reads environment variables (from `.env`); secrets are not in Git.
29. **What does `activity_log` do?** Stores each XP change/badge for the recent-activity list and progress history.
30. **How does the teacher see class analytics?** SQL aggregate queries (COUNT, AVG, GROUP BY) feed Chart.js charts.

## B. Programming / Python (31–45)
31. **What is Python?** A high-level interpreted language; we use Python 3.11.
32. **What is a function?** A reusable block of code, e.g. `calculate_level(xp)`.
33. **Difference between list and dictionary?** A list is ordered by index; a dictionary maps keys to values. DB rows are returned as dictionaries.
34. **What is a tuple?** An immutable sequence; used for SQL parameters `(user_id,)`.
35. **What is a decorator?** A function that wraps another; `@login_required` wraps a route.
36. **What is exception handling?** `try/except` catches errors, e.g. `pymysql.IntegrityError` on duplicate insert.
37. **What is a module?** A Python file we import, e.g. `utils.gamification`.
38. **What is a virtual environment?** An isolated Python environment for project dependencies.
39. **What is `requirements.txt`?** The list of dependencies installed with `pip install -r`.
40. **What is a loop? Where used?** Repeats code; `check_badges` loops over badges, templates loop over lessons.
41. **What is a conditional?** `if/elif/else`; e.g. next_streak's rules.
42. **What does `//` do?** Integer (floor) division: `250 // 100 = 2`.
43. **What is a list comprehension?** Compact list creation, e.g. `[r["name"] for r in rows]`.
44. **What is `__name__ == "__main__"`?** Runs code only when the file is executed directly (starts the dev server).
45. **Why a pure function like `next_streak`?** It depends only on its inputs so it is easy to test.

## C. OOP (46–55) — only what is relevant
46. **What is a class/object?** A class is a blueprint; an object is an instance. Flask itself is a class (`Flask(__name__)`) and our app is an object.
47. **Does EcoQuest define its own classes?** The code is function/module based. Database entities act as the domain model (see class diagram). We use library classes (Flask, Blueprint, connection/cursor objects).
48. **What is encapsulation?** Bundling data with methods and hiding details; our helper modules hide SQL details behind functions (`get_db`, `fetch_all`).
49. **What is a Blueprint?** A Flask object grouping related routes (student, quiz...).
50. **Inheritance example?** Jinja templates: `{% extends "base.html" %}` reuses the layout (template inheritance).
51. **Polymorphism?** Same method name, different behaviour; e.g. `cursor.execute` works with any SQL. Not heavily used in our code.
52. **Abstraction?** The route calls `record_activity()` without knowing how XP/streak/badges are computed.
53. **Why not use an ORM like SQLAlchemy?** Raw SQL with PyMySQL is closer to the syllabus (SQL) and easier to explain.
54. **What is a context manager?** `with conn.cursor() as cur:` closes the cursor automatically.
55. **What is the difference between function and method?** A method belongs to a class/object (`cursor.execute`), a function stands alone.

## D. Database (56–75)
56. **What is a DBMS?** Software to store, manage and query data; MySQL here.
57. **What is SQL?** The language to define and query relational data.
58. **Primary key?** Uniquely identifies a row, e.g. `user_id`.
59. **Foreign key?** A column referencing another table's key, e.g. `quizzes.topic_id → topics.topic_id`.
60. **What is referential integrity?** The DB rejects rows that reference non-existent parents (tested in TC-46).
61. **What is `ON DELETE CASCADE`?** Deleting a parent deletes its children (delete a topic → its lessons go).
62. **What is UNIQUE?** Prevents duplicates, e.g. `users.email`.
63. **What is NOT NULL?** Column must have a value.
64. **What is an index?** A structure that speeds lookups/sorting, e.g. index on `total_xp`.
65. **What is normalization?** Organising tables to reduce redundancy. Quiz→Question→Option is a normalised split.
66. **Which normal form?** Designed to 3NF, with deliberate denormalised `total_xp`/`streak` and newline-separated `key_points`.
67. **INNER JOIN vs LEFT JOIN?** INNER returns only matches; LEFT keeps all left rows (used to show quizzes with zero attempts).
68. **What is GROUP BY?** Groups rows to apply aggregates, e.g. attempts per quiz.
69. **Aggregate functions?** COUNT, SUM, AVG, MIN, MAX — used in dashboards.
70. **ORDER BY?** Sorts results; leaderboard uses `ORDER BY total_xp DESC`.
71. **WHERE vs HAVING?** WHERE filters rows before grouping; HAVING filters groups.
72. **What is a transaction?** A group of statements that commit or roll back together. We commit once per user action.
73. **What are ACID properties?** Atomicity, Consistency, Isolation, Durability; InnoDB supports them.
74. **Why InnoDB?** It supports foreign keys and transactions.
75. **What is a many-to-many relationship?** Users ↔ Badges, implemented by the junction table `user_badges`.

## E. Web (76–85)
76. **Client/server model?** The browser (client) requests pages; Flask (server) responds.
77. **What is HTTP?** The request/response protocol of the web.
78. **GET vs POST?** GET reads data; POST submits data that changes state (login, completing a lesson).
79. **What are HTTP status codes used?** 200 OK, 302 redirect, 400 bad request, 401 unauthorised login, 404 not found.
80. **What is a session?** Per-user data kept between requests, identified by a signed cookie.
81. **What is a cookie?** Small data stored by the browser; Flask's session cookie is signed with `SECRET_KEY`.
82. **What is HTML?** Markup defining page structure.
83. **What is CSS?** Styles the HTML; we use CSS variables, grid/flexbox and media queries.
84. **What is JavaScript used for?** Quiz navigation, menu toggle, charts, confirmations.
85. **What is responsive design?** Layout adapts to screen size via media queries (checked at 375 px width).

## F. Flask (86–95)
86. **What is a route?** A URL mapped to a Python function via `@bp.route`.
87. **What is `render_template`?** Renders a Jinja2 template into HTML.
88. **What is `request.form`?** Dictionary of submitted form data.
89. **What is `redirect`/`url_for`?** Sends the browser to another route; `url_for` builds the URL from the function name.
90. **What is `flash`?** One-time message shown on the next page (XP/badge notifications).
91. **What is `g`?** Per-request storage; we keep the DB connection there.
92. **What is `before_request`?** A hook that runs before each request; we validate the CSRF token.
93. **What is CSRF?** An attack that makes a logged-in user's browser submit unwanted requests; defended by a secret token in each form.
94. **What is SQL injection and how do you prevent it?** Malicious input altering a query; prevented using parameterised queries (`%s`).
95. **What is XSS and how handled?** Injecting scripts via input; Jinja2 auto-escapes output.

## G. Software engineering (96–110)
96. **What is SDLC?** Phases: requirements, design, implementation, testing, deployment, maintenance.
97. **What is Agile?** Iterative, incremental delivery with continuous feedback.
98. **What is an SRS?** Document stating what the system must do (functional/non-functional requirements).
99. **Functional vs non-functional?** What the system does vs qualities (security, usability, performance).
100. **What is UML?** A standard visual notation (use case, class, sequence, activity diagrams).
101. **What is a DFD?** Shows how data flows between processes, stores and external entities.
102. **Level 0 vs Level 1 DFD?** Level 0 shows the whole system as one process; Level 1 breaks it into main processes.
103. **What is an ER diagram?** Shows entities, attributes and relationships of the database.
104. **Types of testing?** Unit, integration, system, acceptance; our pytest tests mix unit tests (level/XP) and integration tests (routes + DB).
105. **What is a test case?** Steps with expected result; ours are in `docs/testing.md`.
106. **What is regression testing?** Re-running tests after changes to ensure nothing broke.
107. **What is maintenance?** Fixing bugs and improving software after release.
108. **What is risk management?** Identifying risks and planning mitigation (see proposal).
109. **What is version control?** Tracking changes with Git; GitHub hosts the repository.
110. **What is feasibility study?** Checking technical, economic, operational and schedule viability.
111. **What is deployment?** Making the application run on a server; prepared for Railway with `gunicorn`.
112. **Why a separate test database?** Tests delete and recreate data; it protects demo/real data.
113. **How is EcoQuest gamified, beyond points?** Eco City that gets cleaner with each level, daily quests with a bonus, timed mini-games with combos, quiz instant feedback, badges, streaks and a leaderboard.
114. **How does the Eco City work?** `city_stage(level)` returns pollution = max(5, 95 − 10×(level−1)) and a scene/name; the dashboard shows it with a progress bar.
115. **How do daily quests work?** `daily_quests()` checks `activity_log` for today's lesson, quiz, challenge and game; when all four exist, `record_activity()` adds a +25 XP bonus once per day.
116. **How are the mini-games protected from cheating?** The server picks the items, stores them in the session and re-grades the submitted answers; XP can be earned once per game per day. It is a casual game, so this is practical rather than absolute protection.
117. **How does quiz instant feedback stay fair?** The browser asks `/quiz/<id>/check`; the first choice for each question is locked in the session and that locked choice is what is graded on submit.
118. **How is a level-up detected?** `record_activity()` compares the level before and after adding XP and returns `level_up`; `flash_rewards()` shows the message.
